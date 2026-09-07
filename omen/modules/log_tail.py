"""Log tailing and filtering utilities for OMEN."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Iterator, Optional

LEVEL_COLORS = {
    "ERROR": "red",
    "CRITICAL": "red",
    "WARNING": "yellow",
    "WARN": "yellow",
    "INFO": "cyan",
    "DEBUG": "white",
}

_LEVEL_PATTERN = re.compile(r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL)\b", re.IGNORECASE)


def detect_level(line: str) -> Optional[str]:
    """Best-effort detection of a log level keyword in a line."""
    match = _LEVEL_PATTERN.search(line)
    if not match:
        return None
    return match.group(1).upper()


def tail_file(path: str, poll_interval: float = 0.5, on_idle=None) -> Iterator[str]:
    """
    Yield new lines appended to `path`, similar to `tail -f`.
    Starts at the end of the file, does not replay existing content.

    If `on_idle` is given, it's called once per poll while waiting for new
    content (no new line available yet) — used by the CLI to drive a
    waiting-state spinner without interleaving it with printed lines.
    """
    file_path = Path(path)
    with open(file_path, "r", errors="ignore") as fh:
        fh.seek(0, 2)  # seek to end
        while True:
            line = fh.readline()
            if line:
                yield line.rstrip("\n")
            else:
                if on_idle is not None:
                    on_idle()
                time.sleep(poll_interval)


def filter_lines(lines: Iterator[str], level: Optional[str] = None) -> Iterator[str]:
    """Filter an iterator of log lines by minimum/matching level."""
    if level is None:
        yield from lines
        return

    level = level.upper()
    for line in lines:
        detected = detect_level(line)
        if detected and detected.startswith(level[:4]):
            yield line
        elif detected == level:
            yield line
