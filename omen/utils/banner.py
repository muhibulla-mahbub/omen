"""
OMEN startup banner animation.

Two pieces:
1. `play_boot_loader()` — a short Braille-spinner boot sequence, meant to run
   once at CLI startup (bounded duration, never blocks forever).
2. `render_live_dashboard()` — the full animated OMEN logo with a shuffling
   glitch effect, meant for `omen banner` (a standalone preview/demo command)
   since it runs until the user presses Ctrl+C.
"""

from __future__ import annotations

import random
import sys
import time

_CLEAR = "\x1b[H\x1b[J"
_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"
_RESET = "\x1b[0m"

_PURPLE = "\x1b[38;2;160;60;240m"
_CYAN = "\x1b[38;2;0;255;190m"

_OMEN_BASE = [
    r"   ____  __  __ _____ _   _ ",
    r"  / __ \|  \/  |  ___| \ | |",
    r" | |  | | |\/| | |__ |  \| |",
    r" | |__| | |  | | |___| |\  |",
    r"  \____/|_|  |_|_____|_| \_|",
]

_SHUFFLE_CHARS = ["/", "\\", "_", "|", "-", "[", "]", "▄", "▀", "█"]

_BRAILLE_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def _clear_screen() -> None:
    sys.stdout.write(_CLEAR)
    sys.stdout.flush()


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
    Render the animated OMEN logo with a glitch/shuffle effect, plus a fixed
    status panel below it. Runs until interrupted with Ctrl+C — intended for
    a standalone `omen banner` preview command, not for every CLI invocation.
    """
    line_1 = " [!] OMEN SECURITY PROTOCOLS INITIATED..."
    line_2 = " [!] ACCESS GRANTED. WELCOME TO OMEN TERMINAL."
    border = " ------------------------------------------------"

    sys.stdout.write(_HIDE_CURSOR)
    sys.stdout.write("\n" * 10)
    sys.stdout.flush()

    try:
        while True:
            sys.stdout.write("\x1b[10A")

            for line in _OMEN_BASE:
                styled_line = ""
                for char in line:
                    if char in ["_", "/", "\\", "|"]:
                        if random.random() < 0.15:
                            styled_line += f"{_CYAN}{random.choice(_SHUFFLE_CHARS)}"
                        else:
                            styled_line += f"{_PURPLE}{char}"
                    elif char != " ":
                        styled_line += f"{_CYAN}{char}"
                    else:
                        styled_line += " "
                sys.stdout.write(f"\r{styled_line}{_RESET}       \n")

            sys.stdout.write(f"\r\n{border}\n")
            sys.stdout.write(f"\r\x1b[1;37m{line_1}{_RESET}\n")
            sys.stdout.write(f"\r\x1b[1;32m{line_2}{_RESET}\n")
            sys.stdout.write(f"\r{border}\n")

            sys.stdout.flush()
            time.sleep(0.08)
    except KeyboardInterrupt:
        sys.stdout.write("\x1b[10A\x1b[J")
        sys.stdout.flush()
        print(f" {_CYAN}[+]{_RESET} OMEN PIPELINE DISCONNECTED. TERMINAL CLEANUP COMPLETE.")
        print(f" \x1b[1;37mOMEN_USER@OS:~# {_RESET}")
    finally:
        sys.stdout.write(_SHOW_CURSOR)
        sys.stdout.flush()


def play_banner(speed: float = 1.0, skip_if_not_tty: bool = True, loop: bool = False) -> None:
    """
    Backwards-compatible entry point used by `cli.py` at startup.
    Plays the bounded boot-loader spinner (never the infinite live dashboard,
    which would hang every command until Ctrl+C).
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
