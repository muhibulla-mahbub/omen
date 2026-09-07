"""
Reusable terminal spinners and progress bar for OMEN commands.

- Spinner: a generic context-manager spinner (any frame set + label).
- BRAILLE_BLOCKS_FRAMES: used by `omen secret scan` while indexing files
  (heavier/"deep scan" feel).
- FLORAL_FRAMES: used by `omen log tail` while waiting for new lines
  (calm, non-intrusive — meant for long-running/idle waits).
- ProgressBar: a bounded progress bar, used by `omen secret scan` while
  scanning a known number of files.

All of these degrade gracefully (print nothing fancy, just do the work)
when stdout isn't a real terminal, so piping/redirecting output or running
in CI never hangs or produces garbled escape codes.
"""

from __future__ import annotations

import sys
import threading
import time
from typing import Optional

_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"
_RESET = "\x1b[0m"
_CYAN = "\x1b[36m"
_GREEN = "\x1b[32m"

BRAILLE_BLOCKS_FRAMES = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
FLORAL_FRAMES = ["·", "✻", "✽", "✶", "✳", "✢"]


class Spinner:
    """
    A simple threaded terminal spinner, usable as a context manager:

        with Spinner(BRAILLE_BLOCKS_FRAMES, "Indexing files..."):
            do_slow_setup()

    No-ops cleanly when stdout is not a tty (piped output, CI logs).
    """

    def __init__(self, frames: list[str], label: str, interval: float = 0.08):
        self.frames = frames
        self.label = label
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._is_tty = sys.stdout.isatty()

    def _spin(self) -> None:
        idx = 0
        while not self._stop_event.is_set():
            frame = self.frames[idx % len(self.frames)]
            sys.stdout.write(f"\r  {_CYAN}{frame}{_RESET} {self.label}")
            sys.stdout.flush()
            idx += 1
            time.sleep(self.interval)

    def __enter__(self) -> "Spinner":
        if self._is_tty:
            sys.stdout.write(_HIDE_CURSOR)
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._is_tty:
            self._stop_event.set()
            if self._thread:
                self._thread.join(timeout=1)
            # Clear the spinner line
            sys.stdout.write("\r" + " " * (len(self.label) + 6) + "\r")
            sys.stdout.write(_SHOW_CURSOR)
            sys.stdout.flush()


class TickSpinner:
    """
    A manually-advanced spinner for use inside polling loops (e.g. `omen log
    tail`'s wait-for-new-lines loop), where a threaded Spinner would race
    with lines being printed from the same loop.

    Call `.tick()` once per poll. Call `.clear()` before printing anything
    else, so the spinner line doesn't get left behind or overwritten badly.
    """

    def __init__(self, frames: list[str], label: str):
        self.frames = frames
        self.label = label
        self._idx = 0
        self._is_tty = sys.stdout.isatty()
        self._active = False

    def tick(self) -> None:
        if not self._is_tty:
            return
        frame = self.frames[self._idx % len(self.frames)]
        sys.stdout.write(f"\r  {_CYAN}{frame}{_RESET} {self.label}")
        sys.stdout.flush()
        self._idx += 1
        self._active = True

    def clear(self) -> None:
        if not self._is_tty or not self._active:
            return
        sys.stdout.write("\r" + " " * (len(self.label) + 6) + "\r")
        sys.stdout.flush()
        self._active = False


class ProgressBar:
    """
    A bounded progress bar for a known total amount of work:

        bar = ProgressBar(total=500, label="Scanning files")
        for i, file in enumerate(files):
            scan(file)
            bar.update(i + 1)
        bar.finish()

    Renders like: [▓▓▓▓▓░░░░░] 45%
    No-ops (prints nothing) when stdout is not a tty.
    """

    def __init__(self, total: int, label: str = "", width: int = 30):
        self.total = max(total, 1)
        self.label = label
        self.width = width
        self._is_tty = sys.stdout.isatty()
        if self._is_tty:
            sys.stdout.write(_HIDE_CURSOR)

    def update(self, current: int) -> None:
        if not self._is_tty:
            return
        fraction = min(current / self.total, 1.0)
        filled = int(self.width * fraction)
        bar = "▓" * filled + "░" * (self.width - filled)
        percent = int(fraction * 100)
        prefix = f"{self.label} " if self.label else ""
        sys.stdout.write(f"\r{prefix}[{bar}] {percent}%")
        sys.stdout.flush()

    def finish(self, message: Optional[str] = None) -> None:
        if not self._is_tty:
            if message:
                print(message)
            return
        self.update(self.total)
        sys.stdout.write("\n")
        if message:
            sys.stdout.write(f"{_GREEN}✔{_RESET} {message}\n")
        sys.stdout.write(_SHOW_CURSOR)
        sys.stdout.flush()
