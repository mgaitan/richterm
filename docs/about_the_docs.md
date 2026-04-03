# About this documentation

This documentation is built using [Sphinx](https://www.sphinx-doc.org/)
with [myst-parser](https://myst-parser.readthedocs.io/).

The theme used is
[sphinx-book-theme](https://sphinx-book-theme.readthedocs.io/en/stable/).

## How to contribute

The documentation is written in [MyST Markdown](https://myst-parser.readthedocs.io/en/latest/syntax/typography.html).

The MyST extensions
[colon_fences](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#code-fences-using-colons),
[linkify](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#linkify),
and [deflist](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#definition-lists) are enabled, and you can also use the extra [content blocks](https://sphinx-book-theme.readthedocs.io/en/stable/content/content-blocks.html)
from our theme.

In addition, you can use all the [directives available in Sphinx](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html),
as explained in [this guide](https://myst-parser.readthedocs.io/en/v4.0.0/using/intro.html#intro-writing).

We also ship [richterm](https://github.com/mgaitan/richterm) to capture CLI output as SVG in the docs.

## Including diagrams

We support [Mermaid diagrams](https://mermaid.js.org/), powered by [sphinxcontrib-mermaid](https://github.com/mgaitan/sphinxcontrib-mermaid):

```{mermaid}
:align: center
graph LR;
    Hi-->there;
```

with this syntax:

````md
```{mermaid}
:align: center
graph LR;
  Hi-->there;
```
````

## Linking to the repo

There is a shortcut for links to the GitHub repository by prefixing `gh:` plus the
relative path. For example:

```md
[ci workflow](gh:.github/workflows/ci.yml)
```

Produces this link: [ci workflow](gh:.github/workflows/ci.yml)

Check `myst_url_schemes` at [docs/conf.py](gh:docs/conf.py) for details on how it is implemented.

## How to build the documentation

From the project root run:

```bash
make docs
```

This runs `sphinx-build` using `uv run` with the docs requirements.
It should exit without errors or warnings.

If you want to check everything looks right in a browser, run:

```bash
make docs-open
```

You can also build EPUB output with `make docs-epub`.

## How the documentation is published online

- GitHub Actions workflow: [`.github/workflows/cd.yml`](gh:.github/workflows/cd.yml) publishes docs to GitHub Pages.
- Triggers:
  - on releases,
  - on pull requests that change docs-related files, publishing a preview under `/_preview/pr-<PR_NUMBER>/`,
  - manually via `workflow_dispatch`.
- To trigger it manually from your repo: `gh workflow run cd.yml --ref main` or use the Actions UI.
