# richterm

`richterm` turns arbitrary terminal commands into Rich-rendered SVG transcripts. Use it from the command line or embed live terminal captures in Sphinx documentation.

## Command-line quick start

Run without installing anything permanently:

```bash
uvx richterm -- python -m rich --force-terminal example
```

Key options:

- `--prompt`: Rich markup shown before the command (defaults to `$`).
- `--hide-command`: omit the prompt/command from the SVG.
- `-o/--output`: select the SVG destination; otherwise `rich_term_<TIMESTAMP>.svg` is created in the working directory.

Rich output is encouraged automatically: unless you opt out, the command runs with colour-friendly hints (`TERM`, `FORCE_COLOR`, `CLICOLOR_FORCE`, `PY_COLORS`, `TTY_COMPATIBLE`).
Set `RICHTERM_DISABLE_COLOR_HINT=1` or export `NO_COLOR` to skip these tweaks.

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
```

Use the directive inside MyST Markdown (or reStructuredText):

````md
```{richterm} python -m rich --force-terminal rainbow
```
````

The directive executes the command during the build, embeds the SVG directly in HTML output, and falls back to a literal code block elsewhere. Override the prompt per block with ``:prompt:`` or hide the command with ``:hide-command:``.

## Example capture

Below is a live capture rendered during the documentation build:

```{richterm} python -m rich --force-terminal tree
```


```{toctree}
:maxdepth: 2
:caption: Documentation

../CONTRIBUTING.md
../CODE_OF_CONDUCT.md
```
