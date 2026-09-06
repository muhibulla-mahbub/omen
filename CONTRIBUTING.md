# Contributing to OMEN

Thanks for your interest in contributing!

## Adding a new module

1. Create your module under `omen/modules/your_module.py`
2. Register a new command/group in `omen/cli.py`
3. Add tests under `tests/`
4. Open a pull request

## Development setup

```bash
git clone https://github.com/muhibulla-mahbub/omen.git
cd omen
pip install -e .
pip install pytest
```

## Running tests

```bash
pytest tests/ -v
```

## Code style

- Keep CLI output colorful but readable (`click.secho` with `fg=`)
- New commands should support `--output json` where it makes sense, for piping into other tools
- Avoid adding heavy dependencies — this is meant to be a lightweight, fast CLI
