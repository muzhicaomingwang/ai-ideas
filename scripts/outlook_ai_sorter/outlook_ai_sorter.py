import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import msal
import requests
import yaml

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
DEFAULT_SCOPES = ["Mail.ReadWrite", "MailboxSettings.ReadWrite"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _read_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def _write_json(path: str, data: Any) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


@dataclass(frozen=True)
class TokenConfig:
    client_id: str
    tenant_id: str = "common"
    scopes: Tuple[str, ...] = tuple(DEFAULT_SCOPES)
    cache_path: str = os.path.join(os.path.dirname(__file__), ".outlook_token_cache.bin")


class StaticTokenProvider:
    def __init__(self, access_token: str):
        token = (access_token or "").strip()
        if not token:
            raise RuntimeError("Empty OUTLOOK_ACCESS_TOKEN.")
        # Microsoft Graph access tokens are typically JWTs (header.payload.signature).
        # If you see a token starting with "EwB..." it's usually an Outlook/Exchange token
        # and will not work with graph.microsoft.com.
        if "." not in token:
            raise RuntimeError(
                "OUTLOOK_ACCESS_TOKEN does not look like a Microsoft Graph JWT. "
                "Use Graph Explorer (developer.microsoft.com/graph/graph-explorer) to copy an Access Token "
                "for resource 'https://graph.microsoft.com' with Mail.ReadWrite/MailboxSettings.ReadWrite."
            )
        self._token = token

    def get_access_token(self) -> str:
        return self._token


class TokenProvider:
    def __init__(self, cfg: TokenConfig):
        self.cfg = cfg
        self.cache = msal.SerializableTokenCache()
        if os.path.exists(cfg.cache_path):
            self.cache.deserialize(open(cfg.cache_path, "r", encoding="utf-8").read())
        self.app = msal.PublicClientApplication(
            client_id=cfg.client_id,
            authority=f"https://login.microsoftonline.com/{cfg.tenant_id}",
            token_cache=self.cache,
        )

    def _persist_cache(self) -> None:
        if self.cache.has_state_changed:
            with open(self.cfg.cache_path, "w", encoding="utf-8") as f:
                f.write(self.cache.serialize())

    def get_access_token(self) -> str:
        accounts = self.app.get_accounts()
        result: Optional[Dict[str, Any]] = None
        if accounts:
            result = self.app.acquire_token_silent(list(self.cfg.scopes), account=accounts[0])
        if not result:
            flow = self.app.initiate_device_flow(scopes=list(self.cfg.scopes))
            if "message" not in flow:
                raise RuntimeError(f"Failed to start device flow: {flow}")
            print(flow["message"])
            result = self.app.acquire_token_by_device_flow(flow)

        if not result or "access_token" not in result:
            raise RuntimeError(f"Failed to acquire token: {result}")
        self._persist_cache()
        return result["access_token"]


class GraphClient:
    def __init__(self, token_provider: Any):
        self.token_provider = token_provider

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token_provider.get_access_token()}",
            "Content-Type": "application/json",
        }

    def request(self, method: str, path_or_url: str, *, json_body: Any = None, params: Dict[str, Any] = None) -> Any:
        url = path_or_url if path_or_url.startswith("http") else f"{GRAPH_BASE}{path_or_url}"
        for attempt in range(8):
            resp = requests.request(method, url, headers=self._headers(), json=json_body, params=params, timeout=60)
            if resp.status_code in (429, 503, 504):
                delay = int(resp.headers.get("Retry-After", "0")) or min(2 ** attempt, 30)
                time.sleep(delay)
                continue
            if resp.status_code >= 400:
                hint = ""
                if resp.status_code in (401, 403):
                    hint = (
                        "\nHint: This usually means the token is not a Microsoft Graph token (wrong audience), "
                        "or it lacks delegated permissions. For Graph Explorer tokens, ensure you've consented "
                        "to Mail.ReadWrite and MailboxSettings.ReadWrite, then copy a fresh Access Token."
                    )
                raise RuntimeError(f"Graph error {resp.status_code}: {resp.text}{hint}")
            if resp.status_code == 204:
                return None
            return resp.json()
        raise RuntimeError(f"Graph request failed after retries: {method} {url}")

    def get(self, path: str, *, params: Dict[str, Any] = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json_body: Any) -> Any:
        return self.request("POST", path, json_body=json_body)


def iter_paged(client: GraphClient, path: str, *, params: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    data = client.get(path, params=params)
    while True:
        for item in data.get("value", []):
            yield item
        next_link = data.get("@odata.nextLink")
        if not next_link:
            break
        data = client.request("GET", next_link)


def _addr(msg: Dict[str, Any]) -> str:
    return ((msg.get("from") or {}).get("emailAddress") or {}).get("address") or ""


def _domain(address: str) -> str:
    address = (address or "").strip().lower()
    return address.split("@", 1)[1] if "@" in address else ""


def _headers_map(msg: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for h in msg.get("internetMessageHeaders") or []:
        name = (h.get("name") or "").strip()
        if not name:
            continue
        out[name.lower()] = (h.get("value") or "").strip()
    return out


def _match_rule(msg: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    match = rule.get("match") or {}
    address = _addr(msg).lower()
    subject = (msg.get("subject") or "").lower()
    headers = _headers_map(msg)

    def any_contains(hay: str, needles: List[str]) -> bool:
        return any((n or "").lower() in hay for n in needles if n)

    from_domains = [d.lower() for d in (match.get("from_domains") or [])]
    if from_domains and _domain(address) not in from_domains:
        return False

    from_contains = [s.lower() for s in (match.get("from_contains") or [])]
    if from_contains and not any_contains(address, from_contains):
        return False

    subject_contains = [s.lower() for s in (match.get("subject_contains") or [])]
    if subject_contains and not any_contains(subject, subject_contains):
        return False

    header_exists = [h.lower() for h in (match.get("header_exists") or [])]
    if header_exists and not any(h in headers for h in header_exists):
        return False

    header_contains = (match.get("header_contains") or {})
    if header_contains:
        for k, v in header_contains.items():
            key = (k or "").lower()
            want = (v or "").lower()
            if key not in headers or want not in (headers.get(key) or "").lower():
                return False

    return True


def classify(msg: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[str, str]:
    for rule in cfg.get("rules") or []:
        if _match_rule(msg, rule):
            name = rule.get("name") or "Matched"
            folder = rule.get("folder") or cfg.get("default_folder") or "Other"
            return name, folder
    return "Default", cfg.get("default_folder") or "Other"


def _find_child_folder(client: GraphClient, parent_id: str, display_name: str) -> Optional[Dict[str, Any]]:
    for f in iter_paged(client, f"/me/mailFolders/{parent_id}/childFolders", params={"$top": 200, "$select": "id,displayName"}):
        if (f.get("displayName") or "").strip().lower() == display_name.strip().lower():
            return f
    return None


def ensure_folder_path(client: GraphClient, parent_id: str, path: str) -> str:
    current_parent = parent_id
    for segment in [p for p in path.split("/") if p.strip()]:
        existing = _find_child_folder(client, current_parent, segment)
        if existing:
            current_parent = existing["id"]
            continue
        created = client.post(f"/me/mailFolders/{current_parent}/childFolders", json_body={"displayName": segment})
        current_parent = created["id"]
    return current_parent


def move_message(client: GraphClient, message_id: str, dest_folder_id: str) -> None:
    client.post(f"/me/messages/{message_id}/move", json_body={"destinationId": dest_folder_id})


def phase1(client: GraphClient, cfg: Dict[str, Any], *, dry_run: bool, state_path: str) -> None:
    state = _read_json(state_path, default={"moved": {}})
    moved: Dict[str, Any] = state.get("moved") or {}

    parent = (cfg.get("review_parent") or "inbox").strip()
    review_root = (cfg.get("review_root") or "AI_Review").strip()
    parent_id = parent
    review_root_id = ensure_folder_path(client, parent_id, review_root)

    older_than_days = int(cfg.get("older_than_days") or 365)
    cutoff = _utc_now() - timedelta(days=older_than_days)
    max_messages = int(cfg.get("max_messages") or 2000)

    params = {
        "$top": 50,
        "$select": "id,subject,from,receivedDateTime,internetMessageHeaders",
        "$orderby": "receivedDateTime asc",
        "$filter": f"receivedDateTime lt {_iso(cutoff)}",
    }

    print(f"Phase1: scanning Inbox messages received before {_iso(cutoff)} (max {max_messages})")
    processed = 0
    stats: Dict[str, int] = {}

    for msg in iter_paged(client, "/me/mailFolders/inbox/messages", params=params):
        if processed >= max_messages:
            break
        msg_id = msg.get("id")
        if not msg_id or msg_id in moved:
            continue

        label, folder_rel = classify(msg, cfg)
        dest_path = f"{review_root}/{folder_rel}".strip("/")
        dest_id = ensure_folder_path(client, parent_id, dest_path)

        address = _addr(msg)
        subject = msg.get("subject") or ""
        received = msg.get("receivedDateTime") or ""

        processed += 1
        stats[dest_path] = stats.get(dest_path, 0) + 1
        print(f"[{processed}] {received} {address} | {subject} -> {dest_path}")

        if not dry_run:
            move_message(client, msg_id, dest_id)
            moved[msg_id] = {"dest": dest_path, "label": label, "from": address, "receivedDateTime": received}

    if not dry_run:
        state["moved"] = moved
        _write_json(state_path, state)

    print("\nPhase1 summary:")
    for k in sorted(stats.keys()):
        print(f"- {k}: {stats[k]}")
    if dry_run:
        print("\n(dry-run) No messages were moved.")
    else:
        print(f"\nState saved to: {state_path}")
        print(f"Review folder: {parent}/'{review_root}' (created if missing)")


def _group_counts(items: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    by_addr: Dict[str, int] = {}
    by_domain: Dict[str, int] = {}
    for it in items:
        addr = (it.get("from") or "").strip().lower()
        if not addr:
            continue
        by_addr[addr] = by_addr.get(addr, 0) + 1
        dom = _domain(addr)
        if dom:
            by_domain[dom] = by_domain.get(dom, 0) + 1
    return by_addr, by_domain


def phase2(client: GraphClient, cfg: Dict[str, Any], *, apply: bool, state_path: str, proposals_path: str) -> None:
    state = _read_json(state_path, default={"moved": {}})
    moved: Dict[str, Any] = state.get("moved") or {}
    if not moved:
        raise RuntimeError(f"No Phase1 state found in {state_path}. Run phase1 first.")

    moved_items = list(moved.values())
    all_by_addr, all_by_domain = _group_counts(moved_items)

    rulegen = cfg.get("rulegen") or {}
    min_count = int(rulegen.get("min_count") or 10)
    min_precision = float(rulegen.get("min_precision") or 0.95)
    allow_domain_rules = bool(rulegen.get("allow_domain_rules") or False)

    parent = (cfg.get("review_parent") or "inbox").strip()
    review_root = (cfg.get("review_root") or "AI_Review").strip()
    parent_id = parent

    folder_cache: Dict[str, str] = {}

    def folder_id_for(dest_path: str) -> str:
        if dest_path not in folder_cache:
            folder_cache[dest_path] = ensure_folder_path(client, parent_id, dest_path)
        return folder_cache[dest_path]

    proposals: List[Dict[str, Any]] = []
    by_dest: Dict[str, List[Dict[str, Any]]] = {}
    for it in moved_items:
        dest = it.get("dest") or ""
        by_dest.setdefault(dest, []).append(it)

    for dest, items in sorted(by_dest.items(), key=lambda kv: len(kv[1]), reverse=True):
        dest_by_addr, dest_by_domain = _group_counts(items)

        for addr, count in sorted(dest_by_addr.items(), key=lambda kv: kv[1], reverse=True):
            if count < min_count:
                break
            precision = count / max(all_by_addr.get(addr, 0), 1)
            if precision < min_precision:
                continue
            proposals.append(
                {
                    "kind": "from_address",
                    "displayName": f"AI: move {addr} -> {dest}",
                    "conditions": {"fromAddresses": [{"emailAddress": {"address": addr}}]},
                    "actions": {"moveToFolder": folder_id_for(dest), "stopProcessingRules": True},
                    "stats": {"count": count, "precision": precision},
                }
            )

        if allow_domain_rules:
            for dom, count in sorted(dest_by_domain.items(), key=lambda kv: kv[1], reverse=True):
                if count < min_count:
                    break
                precision = count / max(all_by_domain.get(dom, 0), 1)
                if precision < min_precision:
                    continue
                proposals.append(
                    {
                        "kind": "from_domain",
                        "displayName": f"AI: move *@{dom} -> {dest}",
                        "conditions": {"senderContains": [f"@{dom}"]},
                        "actions": {"moveToFolder": folder_id_for(dest), "stopProcessingRules": True},
                        "stats": {"count": count, "precision": precision},
                    }
                )

    _write_json(proposals_path, {"generatedAt": _iso(_utc_now()), "proposals": proposals})
    print(f"Wrote {len(proposals)} rule proposals to: {proposals_path}")

    if not apply:
        print("Not applying rules (use --apply to create them in Exchange).")
        return

    if not proposals:
        print("No proposals meet thresholds; nothing to apply.")
        return

    existing = {
        r.get("displayName")
        for r in iter_paged(client, "/me/mailFolders/inbox/messageRules", params={"$top": 200, "$select": "id,displayName"})
    }
    to_create = [p for p in proposals if p.get("displayName") not in existing]
    print(f"Existing rules: {len(existing)}; to create: {len(to_create)}")
    if not to_create:
        return

    confirm = input("Type 'yes' to create these rules in your Inbox: ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    created = 0
    for p in to_create:
        payload = {
            "displayName": p["displayName"],
            "sequence": 1,
            "isEnabled": True,
            "conditions": p["conditions"],
            "actions": p["actions"],
        }
        client.post("/me/mailFolders/inbox/messageRules", json_body=payload)
        created += 1
        print(f"[{created}/{len(to_create)}] created: {p['displayName']}")


def _token_config_from_env() -> TokenConfig:
    client_id = os.environ.get("OUTLOOK_CLIENT_ID", "").strip()
    if not client_id:
        raise RuntimeError("Missing OUTLOOK_CLIENT_ID env var.")
    tenant_id = os.environ.get("OUTLOOK_TENANT_ID", "common").strip() or "common"
    return TokenConfig(client_id=client_id, tenant_id=tenant_id)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("phase1", help="Classify and move messages to a review folder")
    p1.add_argument("--config", required=True, help="Path to config.yml")
    p1.add_argument("--dry-run", action="store_true")
    p1.add_argument(
        "--state",
        default=os.path.join(os.path.dirname(__file__), ".outlook_ai_sorter_state.json"),
        help="State json path (stores moved message ids)",
    )

    p2 = sub.add_parser("phase2", help="Generate (and optionally create) Inbox rules from Phase1 results")
    p2.add_argument("--config", required=True, help="Path to config.yml")
    p2.add_argument("--apply", action="store_true", help="Create rules in Exchange Inbox after confirmation")
    p2.add_argument(
        "--state",
        default=os.path.join(os.path.dirname(__file__), ".outlook_ai_sorter_state.json"),
        help="State json path (reads Phase1 moved results)",
    )
    p2.add_argument(
        "--proposals",
        default=os.path.join(os.path.dirname(__file__), "rule_proposals.json"),
        help="Where to write generated rule proposals",
    )

    args = ap.parse_args()
    cfg = load_config(args.config)

    access_token = os.environ.get("OUTLOOK_ACCESS_TOKEN", "").strip()
    if access_token:
        token_provider = StaticTokenProvider(access_token)
    else:
        token_provider = TokenProvider(_token_config_from_env())
    client = GraphClient(token_provider)

    if args.cmd == "phase1":
        phase1(client, cfg, dry_run=bool(args.dry_run), state_path=args.state)
        return
    if args.cmd == "phase2":
        phase2(client, cfg, apply=bool(args.apply), state_path=args.state, proposals_path=args.proposals)
        return


if __name__ == "__main__":
    main()
