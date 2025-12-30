#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SQL_FENCE_RE = re.compile(r"```sql\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
CREATE_TABLE_RE = re.compile(r"^\s*CREATE\s+TABLE\s+([a-zA-Z_][\w.]*)\s*\(", re.IGNORECASE | re.MULTILINE)
COMMENT_TABLE_RE = re.compile(r"COMMENT\s+ON\s+TABLE\s+([a-zA-Z_][\w.]*)\s+IS\s+", re.IGNORECASE)
COMMENT_COLUMN_RE = re.compile(r"COMMENT\s+ON\s+COLUMN\s+([a-zA-Z_][\w.]*)\s+IS\s+", re.IGNORECASE)


DISALLOWED_PATTERNS = [
    (re.compile(r"\bFOREIGN\s+KEY\b", re.IGNORECASE), "Disallow foreign keys (FOREIGN KEY)"),
    (re.compile(r"\bREFERENCES\b", re.IGNORECASE), "Disallow foreign keys (REFERENCES)"),
    (re.compile(r"\bCREATE\s+UNIQUE\s+INDEX\b", re.IGNORECASE), "Prefer UNIQUE constraints, not CREATE UNIQUE INDEX"),
    (re.compile(r"\bJOIN\b", re.IGNORECASE), "Avoid join-based designs/queries (JOIN)"),
    (re.compile(r"\bAUTO_INCREMENT\b", re.IGNORECASE), "MySQL-only AUTO_INCREMENT; avoid for PostgreSQL"),
]

# Auto-increment/identity markers for PostgreSQL (still discouraged as PK in this convention)
IDENTITY_RE = re.compile(r"\bSERIAL\b|\bGENERATED\s+(?:ALWAYS|BY\s+DEFAULT)\s+AS\s+IDENTITY\b", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    file: Path
    message: str


def iter_markdown_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted([p for p in path.rglob("*.md") if p.is_file()])


def scan_file(file_path: Path) -> list[Finding]:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    sql_blocks = SQL_FENCE_RE.findall(text)

    findings: list[Finding] = []
    created_tables: set[str] = set()
    commented_tables: set[str] = set()
    commented_columns_tables: set[str] = set()

    for block in sql_blocks:
        for regex, message in DISALLOWED_PATTERNS:
            if regex.search(block):
                findings.append(Finding(file=file_path, message=message))

        for table in CREATE_TABLE_RE.findall(block):
            created_tables.add(table)
            # Heuristic: core tables should have create_time/update_time.
            if not re.search(r"\bcreate_time\b", block, re.IGNORECASE):
                findings.append(Finding(file=file_path, message=f"Table `{table}` missing `create_time` column (expected for entity/aggregate root tables)"))
            if not re.search(r"\bupdate_time\b", block, re.IGNORECASE):
                findings.append(Finding(file=file_path, message=f"Table `{table}` missing `update_time` column (expected for entity/aggregate root tables)"))

            # Heuristic: *_id should not be int/bigint if intended as external ID
            for m in re.finditer(r"\b([a-zA-Z_]\w*_id)\b\s+(BIGINT|INT|INTEGER)\b", block, re.IGNORECASE):
                col, typ = m.group(1), m.group(2).upper()
                findings.append(Finding(file=file_path, message=f"Column `{table}.{col}` is {typ}; prefer TEXT prefixed IDs for domain entities"))

            # Discourage identity-as-primary-key
            if IDENTITY_RE.search(block) and re.search(r"\bPRIMARY\s+KEY\b", block, re.IGNORECASE):
                findings.append(Finding(file=file_path, message=f"Table `{table}` appears to use identity/serial; avoid auto-increment primary keys"))

        for table in COMMENT_TABLE_RE.findall(block):
            commented_tables.add(table)
        for col_ref in COMMENT_COLUMN_RE.findall(block):
            # col_ref like table.column
            table = col_ref.split(".", 1)[0]
            commented_columns_tables.add(table)

    for table in sorted(created_tables):
        if table not in commented_tables:
            findings.append(Finding(file=file_path, message=f"Missing `COMMENT ON TABLE {table} ...`"))
        if table not in commented_columns_tables:
            findings.append(Finding(file=file_path, message=f"Missing `COMMENT ON COLUMN {table}.* ...` (no column comments found for this table)"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Markdown SQL snippets for TeamVenture-style PostgreSQL schema conventions.")
    parser.add_argument("path", type=str, help="Markdown file or directory to scan")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 2

    files = iter_markdown_files(root)
    all_findings: list[Finding] = []
    for file in files:
        all_findings.extend(scan_file(file))

    if not all_findings:
        print("OK: no findings")
        return 0

    by_file: dict[Path, list[Finding]] = {}
    for finding in all_findings:
        by_file.setdefault(finding.file, []).append(finding)

    for file, findings in sorted(by_file.items(), key=lambda kv: str(kv[0])):
        print(f"\n{file}")
        for finding in findings:
            print(f"- {finding.message}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
