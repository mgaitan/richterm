# richterm

[![ci](https://github.com/mgaitan/richterm/actions/workflows/ci.yml/badge.svg)](https://github.com/mgaitan/richterm/actions/workflows/ci.yml)
[![docs](https://img.shields.io/badge/docs-blue.svg?style=flat)](https://mgaitan.github.io/richterm/)
[![pypi version](https://img.shields.io/pypi/v/richterm.svg)](https://pypi.org/project/richterm/)
[![Changelog](https://img.shields.io/github/v/release/mgaitan/richterm?include_prereleases&label=changelog)](https://github.com/mgaitan/richterm/releases)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/mgaitan/richterm/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](https://github.com/mgaitan/richterm/blob/main/LICENSE)

`richterm` turns arbitrary terminal commands into Rich-rendered SVG transcripts. Use it from the command line or embed live terminal captures in Sphinx documentation.

## Command-line quick start

Run without installing anything permanently:

```bash
uvx richterm
```

```{richterm} env PYTHONPATH=../src uv run -m richterm --help
:shown-command: uvx richterm --help
```

Key options:

- `--prompt`: Rich markup shown before the command (defaults to `$`).
- `--hide-command`: omit the prompt/command from the SVG.
- `-o/--output`: select the SVG destination; otherwise `rich_term_<TIMESTAMP>.svg` is created in the working directory.
- `--shown-command`: render a different command string than the one executed (useful when the real invocation is noisy or repetitive).

Rich output is encouraged automatically: unless you opt out, the command runs with colour-friendly hints (`TERM`, `FORCE_COLOR`, `CLICOLOR_FORCE`, `PY_COLORS`, `TTY_COMPATIBLE`).
Set `RICHTERM_DISABLE_COLOR_HINT=1` or export `NO_COLOR` to skip these tweaks.

To install the tool permanently:

```bash
uv tool install richterm
```

## Sphinx directive

Enable the extension in ``conf.py``:

```python
extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "richterm.sphinxext",
]
richterm_prompt = "[bold]$"
richterm_hide_command = False
# Optional default text to display instead of the executed command
richterm_shown_command = None
```

Use the directive inside MyST Markdown:

````md
```{richterm} python -m rich --force-terminal rainbow
```
````

Or in reStructuredText:

```rst
.. richterm:: python -m rich --force-terminal rainbow
:shown-command: python -m rich rainbow
```

The directive executes the command during the build, embeds the SVG directly in HTML output, and falls back to a literal code block elsewhere. Override the prompt per block with ``:prompt:``, hide the command with ``:hide-command:``, or swap the displayed command while running another with ``:shown-command:`` (falls back to ``richterm_shown_command`` if set).
If you hide the command, any ``:shown-command:`` value is ignored (a warning is emitted).


```{toctree}
:maxdepth: 2
:caption: Documentation

../CONTRIBUTING.md
../CODE_OF_CONDUCT.md
about_the_docs.md
```
