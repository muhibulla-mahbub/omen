"""Basic secret-scanning module for OMEN — regex-based credential detection."""

from __future__ import annotations

import re
from pathlib import Path

# A small starter set of patterns — expand as needed.
PATTERNS = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Generic API Key": re.compile(r"(?i)api[_-]?key[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']"),
    "GitHub Token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),
    "Slack Token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "Private Key Header": re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----"),
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def scan_path(path: str) -> list[dict]:
    """Scan a file or directory tree for secrets matching known patterns."""
    root = Path(path)
    findings: list[dict] = []

    files = [root] if root.is_file() else _walk_files(root)

    for file_path in files:
        try:
            text = file_path.read_text(errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for rule_name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {
                            "file": str(file_path),
                            "line": line_no,
                            "rule": rule_name,
                        }
                    )
    return findings


def _walk_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            yield p
