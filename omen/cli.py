"""
OMEN — terminal-based security/developer toolkit.
Entry point for the `omen` command.
"""

from __future__ import annotations

import json as json_lib

import click

from omen.utils.banner import play_banner, render_live_dashboard
from omen.utils.config import load_config


@click.group(invoke_without_command=True)
@click.option("--no-banner", is_flag=True, default=False, help="Skip the startup banner animation.")
@click.option("--banner-speed", type=float, default=None, help="Banner animation speed multiplier.")
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default=None,
    help="Output format for commands that support it.",
)
@click.version_option(version="0.2.0", prog_name="omen")
@click.pass_context
def cli(ctx: click.Context, no_banner: bool, banner_speed: float | None, output: str | None) -> None:
    """OMEN — a terminal-native security & developer toolkit."""
    config = load_config()

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["output"] = output or config.get("output_format", "text")

    show_banner = config.get("show_banner", True) and not no_banner
    speed = banner_speed if banner_speed is not None else config.get("banner_speed", 1.0)

    if ctx.invoked_subcommand is None:
        if show_banner:
            play_banner(speed=speed)
        click.echo(ctx.get_help())
    else:
        if show_banner:
            play_banner(speed=max(speed, 2.5))  # snappier when running a real command


@cli.command("banner")
def banner_command() -> None:
    """Play the full animated OMEN logo dashboard (press Ctrl+C to exit)."""
    render_live_dashboard()


# ─────────────────────────── encode ───────────────────────────


@cli.group()
def encode() -> None:
    """Encode or decode strings (base64, hex, URL, ROT13)."""


@encode.command("base64")
@click.argument("text")
@click.option("--decode", "-d", is_flag=True, help="Decode instead of encode.")
def encode_base64_cmd(text: str, decode: bool) -> None:
    """Base64 encode/decode TEXT."""
    from omen.modules.encoder import decode_base64, encode_base64

    try:
        result = decode_base64(text) if decode else encode_base64(text)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Failed: {exc}")
    click.echo(result)


@encode.command("hex")
@click.argument("text")
@click.option("--decode", "-d", is_flag=True, help="Decode instead of encode.")
def encode_hex_cmd(text: str, decode: bool) -> None:
    """Hex encode/decode TEXT."""
    from omen.modules.encoder import decode_hex, encode_hex

    try:
        result = decode_hex(text) if decode else encode_hex(text)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Failed: {exc}")
    click.echo(result)


@encode.command("url")
@click.argument("text")
@click.option("--decode", "-d", is_flag=True, help="Decode instead of encode.")
def encode_url_cmd(text: str, decode: bool) -> None:
    """URL encode/decode TEXT."""
    from omen.modules.encoder import decode_url, encode_url

    result = decode_url(text) if decode else encode_url(text)
    click.echo(result)


@encode.command("rot13")
@click.argument("text")
def encode_rot13_cmd(text: str) -> None:
    """ROT13 TEXT (same operation encodes and decodes)."""
    from omen.modules.encoder import rot13

    click.echo(rot13(text))


# ─────────────────────────── secret ───────────────────────────


@cli.group()
def secret() -> None:
    """Scan files/directories for leaked secrets and credentials."""


@secret.command("scan")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def secret_scan(ctx: click.Context, path: str) -> None:
    """Scan PATH for potential leaked secrets (AWS keys, tokens, private keys, etc)."""
    from omen.modules.secret_scanner import scan_path

    findings = scan_path(path)
    output_format = ctx.obj.get("output", "text")

    if output_format == "json":
        click.echo(json_lib.dumps(findings, indent=2))
        return

    if not findings:
        click.secho("No secrets found.", fg="green")
        return
    for f in findings:
        click.secho(f"[!] {f['file']}:{f['line']} — {f['rule']}", fg="red")
    click.secho(f"\n{len(findings)} potential secret(s) found.", fg="yellow")


# ─────────────────────────── jwt ───────────────────────────


@cli.group()
def jwt() -> None:
    """Decode and inspect JWTs (no signing, no live bypass attempts)."""


@jwt.command("decode")
@click.argument("token")
@click.pass_context
def jwt_decode(ctx: click.Context, token: str) -> None:
    """Decode TOKEN's header and payload, and flag alg=none misconfigurations."""
    from omen.modules.jwt_tool import InvalidTokenError, check_alg_none, decode_jwt

    try:
        decoded = decode_jwt(token)
    except InvalidTokenError as exc:
        raise click.ClickException(str(exc))

    output_format = ctx.obj.get("output", "text")
    if output_format == "json":
        click.echo(json_lib.dumps(decoded, indent=2))
        return

    click.secho("Header:", fg="cyan", bold=True)
    click.echo(json_lib.dumps(decoded["header"], indent=2))
    click.secho("\nPayload:", fg="cyan", bold=True)
    click.echo(json_lib.dumps(decoded["payload"], indent=2))

    if check_alg_none(decoded):
        click.secho(
            "\n[!] WARNING: header declares alg=none — this token would bypass "
            "signature verification on vulnerable libraries.",
            fg="red",
            bold=True,
        )


# ─────────────────────────── log ───────────────────────────


@cli.group()
def log() -> None:
    """Tail and filter log files with colorized output."""


@log.command("tail")
@click.argument("path", type=click.Path(exists=True))
@click.option("--level", type=str, default=None, help="Only show lines matching this log level (e.g. ERROR).")
def log_tail_cmd(path: str, level: str | None) -> None:
    """Tail PATH in real time, colorized by detected log level."""
    from omen.modules.log_tail import LEVEL_COLORS, detect_level, filter_lines, tail_file

    click.secho(f"Tailing {path}... (Ctrl+C to stop)", fg="cyan")
    lines = tail_file(path)
    if level:
        lines = filter_lines(lines, level=level)

    try:
        for line in lines:
            detected = detect_level(line)
            color = LEVEL_COLORS.get(detected, None) if detected else None
            click.secho(line, fg=color)
    except KeyboardInterrupt:
        click.echo("\nStopped.")


@log.command("filter")
@click.argument("path", type=click.Path(exists=True))
@click.option("--level", required=True, type=str, help="Only show lines matching this log level.")
def log_filter_cmd(path: str, level: str) -> None:
    """Filter an existing (non-live) log file by level."""
    from omen.modules.log_tail import LEVEL_COLORS, detect_level

    with open(path, "r", errors="ignore") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            detected = detect_level(line)
            if detected and detected.upper().startswith(level.upper()[:4]):
                color = LEVEL_COLORS.get(detected)
                click.secho(line, fg=color)


# ─────────────────────────── req ───────────────────────────


@cli.group()
def req() -> None:
    """Make HTTP requests from the terminal, with local history."""


@req.command("get")
@click.argument("url")
@click.option("--header", "-H", multiple=True, help="Custom header, format 'Key: Value'. Repeatable.")
@click.pass_context
def req_get(ctx: click.Context, url: str, header: tuple[str, ...]) -> None:
    """Send a GET request to URL."""
    _do_request(ctx, "GET", url, header)


@req.command("post")
@click.argument("url")
@click.option("--header", "-H", multiple=True, help="Custom header, format 'Key: Value'. Repeatable.")
@click.option("--data", "-d", default=None, help="Raw request body.")
@click.pass_context
def req_post(ctx: click.Context, url: str, header: tuple[str, ...], data: str | None) -> None:
    """Send a POST request to URL."""
    _do_request(ctx, "POST", url, header, data=data)


@req.command("history")
@click.option("--limit", default=50, help="Number of recent requests to show.")
@click.pass_context
def req_history(ctx: click.Context, limit: int) -> None:
    """Show recent request history (stored locally, never sent anywhere)."""
    from omen.utils.db import get_recent_requests

    records = get_recent_requests(limit=limit)
    output_format = ctx.obj.get("output", "text")

    if output_format == "json":
        click.echo(json_lib.dumps(records, indent=2))
        return

    if not records:
        click.echo("No history yet.")
        return
    for r in records:
        click.echo(f"[{r['status_code']}] {r['method']} {r['url']}")


def _do_request(
    ctx: click.Context,
    method: str,
    url: str,
    headers: tuple[str, ...],
    data: str | None = None,
) -> None:
    import requests

    from omen.utils.db import save_request

    header_dict = {}
    for h in headers:
        if ":" in h:
            key, _, value = h.partition(":")
            header_dict[key.strip()] = value.strip()

    try:
        resp = requests.request(method, url, headers=header_dict, data=data, timeout=10)
    except requests.RequestException as exc:
        raise click.ClickException(f"Request failed: {exc}")

    config = ctx.obj.get("config", {})
    save_request(
        method=method,
        url=url,
        status_code=resp.status_code,
        response_snippet=resp.text,
        max_rows=config.get("history_max_rows", 50),
    )

    output_format = ctx.obj.get("output", "text")
    if output_format == "json":
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        click.echo(json_lib.dumps({"status_code": resp.status_code, "body": body}, indent=2))
        return

    status_color = "green" if resp.ok else "red"
    click.secho(f"Status: {resp.status_code}", fg=status_color, bold=True)
    click.echo(resp.text[:2000])


def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()
