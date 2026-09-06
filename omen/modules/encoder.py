"""Encoding/decoding utilities for OMEN — base64, hex, URL, ROT13."""

from __future__ import annotations

import base64
import codecs
import urllib.parse


def encode_base64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def decode_base64(text: str) -> str:
    return base64.b64decode(text.encode()).decode(errors="replace")


def encode_hex(text: str) -> str:
    return text.encode().hex()


def decode_hex(text: str) -> str:
    return bytes.fromhex(text).decode(errors="replace")


def encode_url(text: str) -> str:
    return urllib.parse.quote(text)


def decode_url(text: str) -> str:
    return urllib.parse.unquote(text)


def rot13(text: str) -> str:
    return codecs.encode(text, "rot_13")
