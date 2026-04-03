# Getting Started (Tutorial)

This tutorial walks through the main user-facing flow: run `richterm`, generate an SVG, and then install it permanently if you want it around.

## 1. Run `richterm` without installing it

The quickest way to try the tool is with `uvx`:

```bash
uvx richterm echo "hello from richterm"
```

That command runs `echo "hello from richterm"`, renders the transcript as an SVG, and writes a file named like `rich_term_20260403_153000.svg` in the current directory.

## 2. Pick an explicit output path

Use `-o` when you want the SVG somewhere predictable:

```bash
uvx richterm -o demo.svg python -c "print('hello')"
```

## 3. Customize what appears in the transcript

You can tweak the prompt, hide the command, or show a friendlier command than the one actually executed:

```bash
uvx richterm --prompt "[bold blue]$" git status --short
uvx richterm --hide-command python -c "print('secret command')"
uvx richterm --shown-command "pytest -q" python -c "print('fixture output')"
```

## 4. Install it as a tool

If you plan to use `richterm` regularly, install it once:

```bash
uv tool install richterm
```

After that, invoke it directly:

```bash
richterm --help
```

## 5. Run from a local checkout when contributing

If you are working on the project itself, sync the environment and run from source:

```bash
uv sync
uv run richterm --help
```

For module execution from the checkout, you can also use:

```bash
PYTHONPATH=src uv run -m richterm --help
```
