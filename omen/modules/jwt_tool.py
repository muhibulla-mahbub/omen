"""
JWT inspection utilities for OMEN.

This module only DECODES and INSPECTS tokens you already have — it never
signs, forges, or sends tokens anywhere. The "none-algorithm" check flags
whether a token's header claims alg=none (a known misconfiguration some
JWT libraries historically accepted), so you can tell if a token you
control was issued insecurely. It does not attempt to bypass verification
on any live system.
"""

from __future__ import annotations

import base64
import json


class InvalidTokenError(ValueError):
    pass


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt(token: str) -> dict:
    """
    Decode a JWT's header and payload (no signature verification —
    this is an inspection tool, not an auth library).
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("Token does not have 3 segments (header.payload.signature).")

    header_raw, payload_raw, signature_raw = parts

    try:
        header = json.loads(_b64url_decode(header_raw))
        payload = json.loads(_b64url_decode(payload_raw))
    except Exception as exc:  # noqa: BLE001
        raise InvalidTokenError(f"Failed to decode token: {exc}")

    return {
        "header": header,
        "payload": payload,
        "signature_present": bool(signature_raw),
    }


def check_alg_none(decoded: dict) -> bool:
    """Return True if the token's header algorithm is 'none' (case-insensitive)."""
    alg = decoded.get("header", {}).get("alg", "")
    return isinstance(alg, str) and alg.lower() == "none"
