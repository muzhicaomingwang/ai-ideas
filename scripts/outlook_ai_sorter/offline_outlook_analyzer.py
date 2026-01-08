import argparse
import csv
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from glob import glob
from typing import Dict, Iterable, List, Optional, Tuple


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}", re.IGNORECASE)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _epoch_seconds(dt: datetime) -> int:
    return int(dt.timestamp())


def _domain(email: str) -> str:
    email = (email or "").strip().lower()
    return email.split("@", 1)[1] if "@" in email else ""


def _redact_email(email: str) -> str:
    email = (email or "").strip()
    if "@" not in email:
        return email
    local, dom = email.split("@", 1)
    if not local:
        return f"***@{dom}"
    if len(local) <= 2:
        return f"{local[0]}***@{dom}"
    return f"{local[:2]}***@{dom}"


def _guess_outlook_sqlite_paths() -> List[str]:
    base = os.path.expanduser("~/Library/Group Containers/UBF8T346G9.Office/Outlook/Outlook 15 Profiles")
    return sorted(glob(os.path.join(base, "*", "Data", "Outlook.sqlite")))


def _open_db(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


@dataclass(frozen=True)
class Folder:
    id: int
    name: str
    parent_id: int
    special_type: int
    account_uid: int


def _load_folders(con: sqlite3.Connection) -> Dict[int, Folder]:
    cur = con.cursor()
    cur.execute(
        "select Record_RecordID, Folder_Name, Folder_ParentID, Folder_SpecialFolderType, Record_AccountUID from Folders"
    )
    out: Dict[int, Folder] = {}
    for record_id, name, parent_id, special_type, account_uid in cur.fetchall():
        out[int(record_id)] = Folder(
            id=int(record_id),
            name=str(name or ""),
            parent_id=int(parent_id or 0),
            special_type=int(special_type or 0),
            account_uid=int(account_uid or 0),
        )
    return out


def _folder_path(folders: Dict[int, Folder], folder_id: int) -> str:
    parts: List[str] = []
    seen = set()
    current = folder_id
    while current and current not in seen and current in folders:
        seen.add(current)
        folder = folders[current]
        if folder.name:
            parts.append(folder.name)
        current = folder.parent_id
    return "/".join(reversed(parts)) or str(folder_id)


def _special_folders(folders: Dict[int, Folder], special_type: int) -> List[Folder]:
    return [f for f in folders.values() if f.special_type == special_type]


def _iter_messages(
    con: sqlite3.Connection,
    folder_ids: List[int],
    *,
    older_than_epoch: Optional[int],
    limit: Optional[int],
) -> Iterable[Tuple[int, int, str, str, int, int, int]]:
    cur = con.cursor()
    placeholders = ",".join(["?"] * len(folder_ids))
    sql = (
        "select Record_RecordID, Record_FolderID, Message_SenderAddressList, Message_NormalizedSubject, "
        "Message_TimeReceived, Message_Size, Message_HasAttachment "
        f"from Mail where Record_FolderID in ({placeholders})"
    )
    params: List[object] = list(folder_ids)
    if older_than_epoch is not None:
        sql += " and Message_TimeReceived < ?"
        params.append(int(older_than_epoch))
    sql += " order by Message_TimeReceived desc"
    if limit:
        sql += " limit ?"
        params.append(int(limit))
    cur.execute(sql, params)
    while True:
        rows = cur.fetchmany(1000)
        if not rows:
            break
        for row in rows:
            yield (
                int(row[0]),
                int(row[1]),
                str(row[2] or ""),
                str(row[3] or ""),
                int(row[4] or 0),
                int(row[5] or 0),
                int(row[6] or 0),
            )


def _count_messages(con: sqlite3.Connection, folder_ids: List[int], *, older_than_epoch: Optional[int]) -> Dict[str, int]:
    cur = con.cursor()
    placeholders = ",".join(["?"] * len(folder_ids))
    sql = f"select count(*), coalesce(sum(Message_Size), 0) from Mail where Record_FolderID in ({placeholders})"
    params: List[object] = list(folder_ids)
    if older_than_epoch is not None:
        sql += " and Message_TimeReceived < ?"
        params.append(int(older_than_epoch))
    cur.execute(sql, params)
    count, total_size = cur.fetchone()
    return {"count": int(count or 0), "totalSizeBytes": int(total_size or 0)}


def _safe_sender(sender_addr_list: str) -> str:
    sender_addr_list = (sender_addr_list or "").strip()
    if not sender_addr_list:
        return ""
    m = EMAIL_RE.search(sender_addr_list)
    return m.group(0) if m else sender_addr_list.split(";")[0].strip()


def _add_counts(
    sender_counts: Dict[str, int],
    domain_counts: Dict[str, int],
    sender_sizes: Dict[str, int],
    sender: str,
    size: int,
) -> None:
    sender = (sender or "").lower().strip()
    if not sender:
        return
    sender_counts[sender] = sender_counts.get(sender, 0) + 1
    sender_sizes[sender] = sender_sizes.get(sender, 0) + max(int(size or 0), 0)
    dom = _domain(sender)
    if dom:
        domain_counts[dom] = domain_counts.get(dom, 0) + 1


def _top_k(d: Dict[str, int], k: int) -> List[Tuple[str, int]]:
    return sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:k]


def analyze(
    db_path: str,
    *,
    older_than_days: int,
    top_k: int,
    redact: bool,
    csv_path: Optional[str],
    scan_limit: Optional[int],
) -> Dict[str, object]:
    con = _open_db(db_path)
    folders = _load_folders(con)

    inbox_folders = _special_folders(folders, 1)
    sent_folders = _special_folders(folders, 8)
    if not inbox_folders:
        raise RuntimeError("No Inbox folder found (Folder_SpecialFolderType=1).")
    if not sent_folders:
        raise RuntimeError("No Sent folder found (Folder_SpecialFolderType=8).")

    cutoff = _utc_now() - timedelta(days=int(older_than_days))
    cutoff_epoch = _epoch_seconds(cutoff)

    inbox_ids = sorted({f.id for f in inbox_folders})
    sent_ids = sorted({f.id for f in sent_folders})

    inbox_total = _count_messages(con, inbox_ids, older_than_epoch=None)
    inbox_old = _count_messages(con, inbox_ids, older_than_epoch=cutoff_epoch)
    sent_total = _count_messages(con, sent_ids, older_than_epoch=None)
    sent_old = _count_messages(con, sent_ids, older_than_epoch=cutoff_epoch)

    sender_counts: Dict[str, int] = {}
    domain_counts: Dict[str, int] = {}
    sender_sizes: Dict[str, int] = {}

    sample_rows: List[Dict[str, object]] = []
    for record_id, folder_id, sender_addr, subject, received_epoch, size, has_attach in _iter_messages(
        con, inbox_ids + sent_ids, older_than_epoch=cutoff_epoch, limit=scan_limit
    ):
        sender = _safe_sender(sender_addr)
        _add_counts(sender_counts, domain_counts, sender_sizes, sender, size)
        if len(sample_rows) < 30:
            sample_rows.append(
                {
                    "recordId": record_id,
                    "folder": _folder_path(folders, folder_id),
                    "from": _redact_email(sender) if redact else sender,
                    "subject": subject[:160],
                    "receivedEpoch": received_epoch,
                    "size": size,
                    "hasAttachment": bool(has_attach),
                }
            )

    top_senders = _top_k(sender_counts, top_k)
    top_domains = _top_k(domain_counts, top_k)

    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["sender", "domain", "count", "total_size_mb"])
            for sender, count in sorted(sender_counts.items(), key=lambda kv: kv[1], reverse=True):
                total_mb = round(sender_sizes.get(sender, 0) / 1024 / 1024, 2)
                w.writerow([_redact_email(sender) if redact else sender, _domain(sender), count, total_mb])

    result = {
        "dbPath": db_path,
        "olderThanDays": older_than_days,
        "cutoffUtc": cutoff.isoformat(),
        "counts": {
            "inbox": {"total": inbox_total, "olderThanCutoff": inbox_old},
            "sent": {"total": sent_total, "olderThanCutoff": sent_old},
        },
        "folders": {
            "inbox": [{"id": f.id, "name": f.name, "path": _folder_path(folders, f.id)} for f in inbox_folders],
            "sent": [{"id": f.id, "name": f.name, "path": _folder_path(folders, f.id)} for f in sent_folders],
        },
        "topSenders": [
            {
                "sender": (_redact_email(s) if redact else s),
                "count": c,
                "totalSizeMB": round(sender_sizes.get(s, 0) / 1024 / 1024, 2),
            }
            for s, c in top_senders
        ],
        "topDomains": [{"domain": d, "count": c} for d, c in top_domains],
        "sampleMessages": sample_rows,
    }
    return result


def propose_rules(analysis: Dict[str, object], *, min_count: int) -> Dict[str, object]:
    proposals: List[Dict[str, object]] = []
    for it in analysis.get("topSenders", []):
        sender = str(it.get("sender") or "")
        count = int(it.get("count") or 0)
        if count < min_count:
            continue
        dom = _domain(sender)
        folder = f"AI_Review/From/{dom or 'unknown'}"
        proposals.append(
            {
                "displayName": f"Move from {sender} -> {folder}",
                "kind": "from_address",
                "conditions": {"from_contains": [sender]},
                "actions": {"move_to_folder": folder, "stop_processing": True},
                "stats": {"count": count},
            }
        )
    return {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "minCount": min_count,
        "proposals": proposals,
    }


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", help="Path to Outlook.sqlite (defaults to auto-detect)")
    common.add_argument("--older-than-days", type=int, default=365)
    common.add_argument("--top", type=int, default=30)
    common.add_argument("--no-redact", action="store_true", help="Do not redact email addresses in output")
    common.add_argument(
        "--scan-limit",
        type=int,
        default=0,
        help="Max messages to scan (0 = no limit). Scanning more yields more accurate statistics.",
    )

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="Print a summary + optionally write CSV", parents=[common])
    a.add_argument("--csv", help="Write sender summary CSV to this path")
    a.add_argument("--out", help="Write analysis JSON to this path")

    p = sub.add_parser("propose", help="Generate offline rule proposals JSON (manual apply in Outlook)", parents=[common])
    p.add_argument("--min-count", type=int, default=20)
    p.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "rule_proposals.json"))

    args = ap.parse_args()
    guessed = _guess_outlook_sqlite_paths()
    db_path = args.db or (guessed[0] if guessed else "")
    if not db_path or not os.path.exists(db_path):
        raise RuntimeError("Could not find Outlook.sqlite. Pass --db explicitly.")

    redact = not bool(args.no_redact)
    scan_limit = None if int(args.scan_limit or 0) <= 0 else int(args.scan_limit)
    analysis = analyze(
        db_path,
        older_than_days=args.older_than_days,
        top_k=args.top,
        redact=redact,
        csv_path=getattr(args, "csv", None),
        scan_limit=scan_limit,
    )

    if args.cmd == "analyze":
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
        return

    if args.cmd == "propose":
        proposals = propose_rules(analysis, min_count=int(args.min_count))
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(proposals, f, ensure_ascii=False, indent=2)
        print(f"Wrote proposals: {args.out}")
        return


if __name__ == "__main__":
    main()
