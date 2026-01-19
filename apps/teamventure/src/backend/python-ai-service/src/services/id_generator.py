from __future__ import annotations

import uuid

try:
    import ulid  # type: ignore
except Exception:  # pragma: no cover
    ulid = None


def new_prefixed_id(prefix: str) -> str:
    if ulid is not None:
        return f"{prefix}_{ulid.new().str.lower()}"
    return f"{prefix}_{uuid.uuid4().hex}"
