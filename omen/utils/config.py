"""Config file support for OMEN (~/.omen/config.yaml)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path.home() / ".omen" / "config.yaml"

DEFAULTS: dict[str, Any] = {
    "banner_speed": 1.0,
    "show_banner": True,
    "output_format": "text",  # "text" or "json"
    "history_max_rows": 50,
    "request_timeout": 10,       # seconds, for `omen req get/post`
    "log_poll_interval": 0.5,    # seconds, for `omen log tail`
    "secret_scan_skip_dirs": [], # extra directory names to skip, in addition to the built-in list
}


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """
    Load user config from ~/.omen/config.yaml, merged over defaults.
    Falls back to defaults entirely if PyYAML isn't installed or the
    file doesn't exist — config is a nice-to-have, never a hard requirement.
    """
    config = dict(DEFAULTS)

    if not path.exists():
        return config

    try:
        import yaml  # type: ignore
    except ImportError:
        return config

    try:
        with open(path, "r", encoding="utf-8") as fh:
            user_config = yaml.safe_load(fh) or {}
        if isinstance(user_config, dict):
            config.update(user_config)
    except Exception:  # noqa: BLE001
        pass

    return config


def write_default_config(path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Write a starter config file with default values and comments."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = """\
# OMEN configuration
# Full docs: https://github.com/muhibulla-mahbub/omen

banner_speed: 1.0        # animation speed multiplier
show_banner: true        # set to false to always skip the startup banner
output_format: text      # "text" or "json"
history_max_rows: 50     # how many requests to keep in local history
request_timeout: 10      # seconds, for `omen req get/post`
log_poll_interval: 0.5   # seconds, for `omen log tail`
secret_scan_skip_dirs: []  # extra directory names to skip when scanning, e.g. [dist, build]
"""
    path.write_text(content, encoding="utf-8")
