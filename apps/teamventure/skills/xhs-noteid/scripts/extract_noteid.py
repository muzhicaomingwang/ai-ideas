#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
from typing import Iterable, Optional


NOTEID_PATTERNS = [
    re.compile(r"/discovery/item/([0-9a-fA-F]{16,64})"),
    re.compile(r"[?&](?:noteId|note_id)=([0-9a-fA-F]{16,64})"),
]


def extract_noteid(text: str) -> Optional[str]:
    for pattern in NOTEID_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def resolve_short_url(url: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["curl", "-sS", "-L", "-o", "/dev/null", "-w", "%{url_effective}", url],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError("curl not found; install curl or provide the long xiaohongshu.com URL")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise RuntimeError(f"curl failed to resolve short URL{(': ' + stderr) if stderr else ''}")
    resolved = (result.stdout or "").strip()
    return resolved or None


def iter_inputs(args: list[str]) -> Iterable[str]:
    if args:
        yield " ".join(args)
        return
    data = sys.stdin.read()
    if data.strip():
        yield data


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract XiaoHongShu noteId from share text/URLs.")
    parser.add_argument("text", nargs="*", help="Share text or URL (or read from stdin if omitted).")
    parser.add_argument(
        "--no-resolve",
        action="store_true",
        help="Do not attempt to resolve xhslink.com short URLs.",
    )
    ns = parser.parse_args()

    for text in iter_inputs(ns.text):
        noteid = extract_noteid(text)
        if noteid:
            print(noteid)
            return 0

        if not ns.no_resolve and "xhslink.com" in text:
            resolved = resolve_short_url(text.strip())
            if not resolved:
                raise RuntimeError("could not resolve short URL to a long URL")
            noteid = extract_noteid(resolved)
            if noteid:
                print(noteid)
                return 0
            raise RuntimeError(f"resolved URL did not contain a noteId: {resolved}")

    raise RuntimeError("no noteId found; provide a /discovery/item/<noteId> URL or an xhslink.com short URL")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)

