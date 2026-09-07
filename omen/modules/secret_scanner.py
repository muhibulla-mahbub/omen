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


def list_files(path: str, extra_skip_dirs: "list[str] | None" = None) -> list[Path]:
    """
    Return the full list of files under `path` that will be scanned.
    Split out from `scan_path` so callers (e.g. the CLI) can show an
    indexing spinner, then a progress bar over a known file count.

    `extra_skip_dirs` adds directory names to skip on top of the built-in
    SKIP_DIRS set (e.g. from the user's ~/.omen/config.yaml).
    """
    root = Path(path)
    if root.is_file():
        return [root]
    skip_dirs = SKIP_DIRS | set(extra_skip_dirs or [])
    return list(_walk_files(root, skip_dirs))


def scan_file(file_path: Path) -> list[dict]:
    """Scan a single file for secrets matching known patterns."""
    findings: list[dict] = []
    try:
        text = file_path.read_text(errors="ignore")
    except Exception:  # noqa: BLE001
        return findings

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


def scan_path(path: str, extra_skip_dirs: "list[str] | None" = None) -> list[dict]:
    """Scan a file or directory tree for secrets matching known patterns."""
    findings: list[dict] = []
    for file_path in list_files(path, extra_skip_dirs=extra_skip_dirs):
        findings.extend(scan_file(file_path))
    return findings


def _walk_files(root: Path, skip_dirs: "set[str] | None" = None):
    skip_dirs = skip_dirs if skip_dirs is not None else SKIP_DIRS
    for p in root.rglob("*"):
        if p.is_file() and not any(part in skip_dirs for part in p.parts):
            yield p
