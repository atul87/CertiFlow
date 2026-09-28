from __future__ import annotations
import json
from typing import Any


def canonicalize_json(data: Any) -> bytes:
    """
    Deterministic JSON Canonicalization (RFC 8785 subset) for reproducible
    cryptographic hashing and digital signatures across platforms.
    - Keys are recursively sorted lexicographically.
    - No non-essential whitespace.
    - Encoded in strict UTF-8 without byte-order-mark (BOM).
    """
    def _normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            # Exclude the detached proof block itself when preparing payload for signature
            return {k: _normalize(v) for k, v in sorted(obj.items()) if k != "proof"}
        elif isinstance(obj, list):
            return [_normalize(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool)) or obj is None:
            return obj
        else:
            return str(obj)

    normalized = _normalize(data)
    canonical_str = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True
    )
    return canonical_str.encode("utf-8")
