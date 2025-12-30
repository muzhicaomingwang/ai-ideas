from __future__ import annotations

import ulid


def new_prefixed_id(prefix: str) -> str:
    return f"{prefix}_{ulid.new().str.lower()}"

