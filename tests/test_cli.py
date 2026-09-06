from click.testing import CliRunner

from omen.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "--help"])
    assert result.exit_code == 0
    assert "OMEN" in result.output


def test_encode_base64():
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "encode", "base64", "Hello Hacker"])
    assert result.exit_code == 0
    assert result.output.strip() == "SGVsbG8gSGFja2Vy"


def test_encode_base64_decode():
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "encode", "base64", "-d", "SGVsbG8gSGFja2Vy"])
    assert result.exit_code == 0
    assert result.output.strip() == "Hello Hacker"


def test_encode_hex():
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "encode", "hex", "Hi"])
    assert result.exit_code == 0
    assert result.output.strip() == "4869"


def test_encode_hex_roundtrip():
    runner = CliRunner()
    enc = runner.invoke(cli, ["--no-banner", "encode", "hex", "Hi"])
    assert enc.output.strip() == "4869"
    dec = runner.invoke(cli, ["--no-banner", "encode", "hex", "-d", "4869"])
    assert dec.output.strip() == "Hi"


def test_encode_url():
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "encode", "url", "a b&c"])
    assert result.output.strip() == "a%20b%26c"


def test_encode_rot13():
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "encode", "rot13", "Hello"])
    assert result.exit_code == 0
    assert result.output.strip() == "Uryyb"


def test_jwt_decode_flags_alg_none():
    import base64
    import json

    runner = CliRunner()
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"user": "test"}).encode()).rstrip(b"=").decode()
    token = f"{header}.{payload}."

    result = runner.invoke(cli, ["--no-banner", "jwt", "decode", token])
    assert result.exit_code == 0
    assert "alg=none" in result.output


def test_secret_scan_finds_aws_key(tmp_path):
    runner = CliRunner()
    f = tmp_path / "config.env"
    f.write_text("AWS_KEY=AKIAABCDEFGHIJKLMNOP\n")

    result = runner.invoke(cli, ["--no-banner", "secret", "scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "AWS Access Key" in result.output


def test_req_history_empty(tmp_path, monkeypatch):
    import omen.utils.db as db_module

    monkeypatch.setattr(db_module, "DEFAULT_DB_PATH", tmp_path / "history.db")
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-banner", "req", "history"], obj={})
    assert result.exit_code == 0
