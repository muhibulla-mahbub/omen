"""
OMEN startup banner animation.

Two pieces:
1. `play_boot_loader()` — a short Braille-spinner boot sequence, meant to run
   once at CLI startup (bounded duration, never blocks forever).
2. `render_live_dashboard()` — the boxed OMEN logo with a column-by-column
   reveal and typewriter welcome/version lines, meant for `omen banner` (a
   standalone preview/demo command).
"""

from __future__ import annotations

import sys
import time

_CLEAR = "\x1b[H\x1b[J"
_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"

_BRAILLE_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# Boxed logo used by `omen banner` (render_live_dashboard)
_BOX_BANNER = """  ██████╗ ███╗   ███╗███████╗███╗   ██╗
 ██╔═══██╗████╗ ████║██╔════╝████╗  ██║
 ██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║
 ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║
 ╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║
  ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝"""

_WELCOME_TEXT = "Welcome to OMEN CLI"
_VERSION_TEXT = "CLI Version 0.2.0"


def _clear_screen() -> None:
    sys.stdout.write(_CLEAR)
    sys.stdout.flush()


def _typewriter(text: str, delay: float = 0.03) -> None:
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


def play_boot_loader(duration: float = 2.5, label: str = "Booting OMEN Core System...") -> None:
    """
    Play a short Braille-spinner boot sequence. Bounded by `duration`, so it
    always finishes and returns control to the CLI — safe to call at startup.
    """
    if not sys.stdout.isatty():
        # Non-interactive output (piped/CI) — skip animation entirely.
        return

    end_time = time.time() + duration
    idx = 0

    sys.stdout.write(_HIDE_CURSOR)
    try:
        while time.time() < end_time:
            frame = _BRAILLE_FRAMES[idx % len(_BRAILLE_FRAMES)]
            sys.stdout.write(f"\r  \x1b[36m{frame}\x1b[0m {label}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.08)
        sys.stdout.write(f"\r  \x1b[32m✔\x1b[0m OMEN Engine Ready!\n\n")
        sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write("\n")
    finally:
        sys.stdout.write(_SHOW_CURSOR)
        sys.stdout.flush()


def render_live_dashboard() -> None:
    """
    Render the boxed OMEN logo: a bordered box with a typewriter "Welcome to
    OMEN CLI" line, a column-by-column reveal of the logo, and a typewriter
    version line. Intended for the standalone `omen banner` preview command.
    No-ops to a plain printed banner when stdout isn't a real terminal.
    """
    if not sys.stdout.isatty():
        print(_BOX_BANNER)
        print(f"{_WELCOME_TEXT}\n{_VERSION_TEXT}")
        return

    lines = _BOX_BANNER.split("\n")
    max_len = max(len(line) for line in lines)
    padded_lines = [line.ljust(max_len) for line in lines]

    box_width = max_len + 2
    top_border = "┌" + "─" * box_width + "┐"
    bottom_border = "└" + "─" * box_width + "┘"

    try:
        sys.stdout.write(_HIDE_CURSOR)
        _clear_screen()

        print(top_border)

        sys.stdout.write("│ ")
        _typewriter(_WELCOME_TEXT.ljust(box_width - 1) + "│", delay=0.04)

        for i in range(max_len + 1):
            current_frame = "\n".join(
                "│ " + line[:i].ljust(max_len) + " │" for line in padded_lines
            )
            sys.stdout.write("\x1b[H\x1b[2B" + current_frame)
            sys.stdout.flush()
            time.sleep(0.02)

        sys.stdout.write(f"\x1b[H\x1b[{2 + len(lines)}B\n")

        sys.stdout.write("│ ")
        _typewriter(_VERSION_TEXT.ljust(box_width - 1) + "│", delay=0.03)

        print(bottom_border)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
    finally:
        sys.stdout.write(_SHOW_CURSOR)
        sys.stdout.flush()


def play_banner(speed: float = 1.0, skip_if_not_tty: bool = True, loop: bool = False) -> None:
    """
    Backwards-compatible entry point used by `cli.py` at startup.
    Plays the bounded Braille-spinner boot loader (never the boxed banner,
    which is for the standalone `omen banner` command).
    """
    duration = 2.5 / max(speed, 0.1)
    if skip_if_not_tty and not sys.stdout.isatty():
        return
    play_boot_loader(duration=duration)


if __name__ == "__main__":
    # Manual preview: python -m omen.utils.banner
    _clear_screen()
    play_boot_loader(duration=2.5)
    _clear_screen()
    render_live_dashboard()
