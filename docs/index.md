# richterm

[![ci](https://github.com/mgaitan/richterm/actions/workflows/ci.yml/badge.svg)](https://github.com/mgaitan/richterm/actions/workflows/ci.yml)
[![docs](https://img.shields.io/badge/docs-blue.svg?style=flat)](https://mgaitan.github.io/richterm/)
[![pypi version](https://img.shields.io/pypi/v/richterm.svg)](https://pypi.org/project/richterm/)
[![Changelog](https://img.shields.io/github/v/release/mgaitan/richterm?include_prereleases&label=changelog)](https://github.com/mgaitan/richterm/releases)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/mgaitan/richterm/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](https://github.com/mgaitan/richterm/blob/main/LICENSE)

`richterm` turns arbitrary terminal commands into [Rich](https://github.com/Textualize/rich)-rendered SVG transcripts. Use it from the command line or embed live terminal captures in Sphinx documentation.

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
- `--theme`: choose the Rich terminal export theme (`default`, `monokai`, `dimmed-monokai`, `night-owlish`, or `svg-export`).
- `--hide-command`: omit the prompt/command from the SVG.
- `-o/--output`: select the SVG destination; otherwise `rich_term_<TIMESTAMP>.svg` is created in the working directory.
- `--shown-command`: render a different command string than the one executed (useful when the real invocation is noisy or repetitive).

Rich output is encouraged automatically: unless you opt out, the command runs with colour-friendly hints ({term}`TERM`, {term}`FORCE_COLOR`, `CLICOLOR_FORCE`, `PY_COLORS`, `TTY_COMPATIBLE`).
Set {term}`RICHTERM_THEME` to change the default export theme for both the CLI and Sphinx builds.
Set {term}`RICHTERM_DISABLE_COLOR_HINT` to `1` or export {term}`NO_COLOR` to skip these tweaks. If your CI sets {term}`NO_COLOR` but you still want colour, export {term}`FORCE_COLOR` to `1`.

To install the tool permanently:

```bash
uv tool install richterm
```

## Sphinx directive

Enable the extension in `conf.py`:

```python
extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "richterm.sphinxext",
]
richterm_prompt = "[bold]$"
richterm_hide_command = False
richterm_theme = "default"
# Optional default text to display instead of the executed command
richterm_shown_command = None
```

Use the directive inside MyST Markdown:

````md
```{richterm} python -m rich --force-terminal rainbow
:theme: monokai
```
````

Or in reStructuredText:

```rst
.. richterm:: python -m rich --force-terminal rainbow
:theme: monokai
:shown-command: python -m rich rainbow
```

The directive executes the command during the build, embeds the SVG directly in HTML output, and falls back to a literal code block elsewhere. Override the prompt per block with `:prompt:`, choose a terminal palette with `:theme:`, hide the command with `:hide-command:`, or swap the displayed command while running another with `:shown-command:` (falls back to `richterm_shown_command` if set).
If you hide the command, any `:shown-command:` value is ignored and a warning is emitted.

### Same output, different themes

The same ANSI-rich output can be rendered with different terminal themes:

`````{tabs}
````{tab} default
```{richterm} env PYTHONPATH=../src uv run python -c "from rich.console import Console; from rich.table import Table; console = Console(force_terminal=True); table = Table(title='Status'); table.add_column('Name', style='cyan'); table.add_column('State'); table.add_column('Value', justify='right', style='magenta'); table.add_row('build', '[green]ok[/green]', '42'); table.add_row('tests', '[yellow]warn[/yellow]', '3'); table.add_row('deploy', '[red]fail[/red]', '1'); console.print(table)"
:shown-command: python demo.py
:theme: default
```
````

````{tab} monokai
```{richterm} env PYTHONPATH=../src uv run python -c "from rich.console import Console; from rich.table import Table; console = Console(force_terminal=True); table = Table(title='Status'); table.add_column('Name', style='cyan'); table.add_column('State'); table.add_column('Value', justify='right', style='magenta'); table.add_row('build', '[green]ok[/green]', '42'); table.add_row('tests', '[yellow]warn[/yellow]', '3'); table.add_row('deploy', '[red]fail[/red]', '1'); console.print(table)"
:shown-command: python demo.py
:theme: monokai
```
````

````{tab} night-owlish
```{richterm} env PYTHONPATH=../src uv run python -c "from rich.console import Console; from rich.table import Table; console = Console(force_terminal=True); table = Table(title='Status'); table.add_column('Name', style='cyan'); table.add_column('State'); table.add_column('Value', justify='right', style='magenta'); table.add_row('build', '[green]ok[/green]', '42'); table.add_row('tests', '[yellow]warn[/yellow]', '3'); table.add_row('deploy', '[red]fail[/red]', '1'); console.print(table)"
:shown-command: python demo.py
:theme: night-owlish
```
````
`````

## Documentation Map (Diataxis)

This project follows the [Diataxis](https://diataxis.fr/) framework:

- Tutorials: learning-oriented, step-by-step.
- How-to guides: goal-oriented operational procedures.
- Reference: factual, lookup-first technical details.
- Explanation: context, rationale, and design choices.

```{toctree}
:maxdepth: 2
:caption: Tutorials

getting_started.md
```

```{toctree}
:maxdepth: 2
:caption: How-to Guides

development_workflow.md
```

```{toctree}
:maxdepth: 2
:caption: Reference

configuration.md
```

```{toctree}
:maxdepth: 2
:caption: Explanation

about_the_docs.md
```

```{toctree}
:maxdepth: 2
:caption: Project Policies

../CONTRIBUTING.md
../CODE_OF_CONDUCT.md
```
