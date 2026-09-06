# OMEN

A terminal-native security & developer toolkit. No GUI, no web server — just fast, colorful output straight in your terminal.

## Features

- **`omen encode`** — Base64, Hex, URL, ROT13 encode/decode
- **`omen secret scan`** — scan files/directories for leaked secrets (AWS/GitHub/Slack tokens, private keys)
- **`omen jwt decode`** — JWT header/payload inspection, flags `alg=none` misconfigurations
- **`omen log tail` / `omen log filter`** — colorized real-time log tailing and level filtering
- **`omen req get/post`** — quick HTTP requests from the terminal, with local SQLite history (`omen req history`)
- **`omen banner`** — full animated OMEN logo dashboard with a live glitch effect (press Ctrl+C to exit); a short version of this also plays automatically at startup
- **`--output json`** — machine-readable output on supported commands, for piping into other tools
- **`~/.omen/config.yaml`** — persist your preferred banner speed, output format, and history size

## Installation

```bash
pip install git+https://github.com/muhibulla-mahbub/omen.git
```

Or for local development:

```bash
git clone https://github.com/muhibulla-mahbub/omen.git
cd omen
pip install -e .
```

## Usage

```bash
omen                                          # startup banner + help
omen encode base64 "Hello Hacker"             # -> SGVsbG8gSGFja2Vy
omen encode base64 -d "SGVsbG8="               # decode
omen encode hex "Hi"                          # -> 4869
omen encode url "a b&c"                       # -> a%20b%26c
omen encode rot13 "Hello"                     # -> Uryyb

omen secret scan ./my_project/                # scan a directory for leaked secrets
omen --output json secret scan ./my_project/  # JSON output for piping

omen jwt decode eyJhbGciOi...                 # inspect header/payload, flag alg=none

omen log tail /var/log/nginx/access.log       # live colorized tail
omen log tail app.log --level ERROR           # live, only ERROR lines
omen log filter app.log --level ERROR         # filter an existing file

omen req get https://api.github.com           # quick GET request
omen req post https://api.example.com -d '{"a":1}' -H "Content-Type: application/json"
omen req history                              # last 50 requests (stored locally only)

omen banner                                   # full animated logo dashboard (Ctrl+C to exit)

omen --no-banner encode base64 "text"         # skip the startup animation
omen --banner-speed 0.5 encode base64 "text"  # slower banner
```

### Config file

Create `~/.omen/config.yaml` to set persistent defaults:

```yaml
banner_speed: 1.0
show_banner: true
output_format: text   # or "json"
history_max_rows: 50
```

(Requires `pip install omen-cli[config]` for YAML support — otherwise OMEN falls back to defaults.)

## Project structure

```
omen/
├── pyproject.toml
├── omen/
│   ├── cli.py                  # entry point (Click) — wires every subcommand together
│   ├── modules/
│   │   ├── encoder.py          # base64 / hex / url / rot13
│   │   ├── secret_scanner.py   # AWS/GitHub/Slack token + private key detection
│   │   ├── jwt_tool.py         # JWT decode + alg=none inspection
│   │   └── log_tail.py         # log tailing + level filtering
│   └── utils/
│       ├── banner.py           # boot spinner + live logo dashboard (ANSI, no deps)
│       ├── config.py           # ~/.omen/config.yaml loader
│       └── db.py               # local SQLite request history
└── tests/
```

## Contributing

Contributions welcome! Please open an issue or pull request. New modules go under `omen/modules/`, register a subcommand in `omen/cli.py`.

## License

MIT — see [LICENSE](LICENSE).
