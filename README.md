# richterm

[![CI](https://github.com/mgaitan/richterm/actions/workflows/ci.yml/badge.svg)](https://github.com/mgaitan/richterm/actions/workflows/ci.yml)
[![docs](https://img.shields.io/badge/docs-blue.svg?style=flat)](https://mgaitan.github.io/richterm/)
[![pypi version](https://img.shields.io/pypi/v/richterm.svg)](https://pypi.org/project/richterm/)
[![Changelog](https://img.shields.io/github/v/release/mgaitan/richterm?include_prereleases&label=changelog)](https://github.com/mgaitan/richterm/releases)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/mgaitan/richterm/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](https://github.com/mgaitan/richterm/blob/main/LICENSE)

`richterm` turns arbitrary terminal commands into Rich-rendered SVG images. Run it from the command line or embed live captures in Sphinx documentation with a dedicated directive.

## Quick start

Run the CLI without installing anything permanently:

```bash
uvx richterm
```

To install the tool permanently:

```bash
uv tool install richterm
```

Each invocation writes an SVG named `rich_term_<TIMESTAMP>.svg` (or the file passed with `-o/--output`) and echoes the command output back to the terminal.

To keep colours vibrant even in non-interactive captures, `richterm` sets friendly defaults: `TERM=xterm-256color` (when missing) plus `FORCE_COLOR=1`, `CLICOLOR_FORCE=1`, `PY_COLORS=1`, and `TTY_COMPATIBLE=1` unless you override them. Opt out with `RICHTERM_DISABLE_COLOR_HINT=1` or by exporting `NO_COLOR`.

## Command-line usage

```
usage: richterm [-h|--hide-command] [-o PATH] [--prompt STR] [--shown-command STR] <command...>
```

- `--hide-command` hides the prompt and command line in the transcript.
- `--prompt` accepts Rich markup and defaults to `$`.
- `-o/--output` selects the SVG path; otherwise a timestamped filename is generated.
- `--shown-command` lets you display a different command than the one executed (handy when a fixture command would distract readers). Cannot be combined with `--hide-command`.

Examples:

```bash
richterm ls -la
richterm --prompt "[bold blue]λ" -o docs/_static/listing.svg git status --short
richterm --hide-command python -c "print('\033[31merror\033[0m')"
richterm --shown-command "pytest -q" python -c "print('actually running something else')"
```

## Sphinx integration

`richterm` optionally works as a [Sphinx](https://www.sphinx-doc.org/) extension. Install the extras and enable it in your `conf.py`:

```bash
uv add richterm[sphinx]
```

```python
# docs/conf.py
extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "richterm.sphinxext",
]
richterm_prompt = "[bold]$"
richterm_hide_command = False
```

Then use the directive in MyST:

````md
```{richterm} python -m rich --force-terminal --no-color-system example
```
````

Or in reStructuredText:

```rst
.. richterm:: python -m rich --force-terminal --no-color-system example
```


The directive executes the command during the build, embeds the SVG directly in HTML output, and falls back to a literal block for non-HTML builders. The `:prompt:` and `:hide-command:` options mirror the CLI flags.

## Development

Tests depend on the Sphinx extras:

```bash
uv run --extra sphinx pytest
```

Or directly `make test`


Build the documentation (which exercises the directive itself):

```bash
make docs
```
