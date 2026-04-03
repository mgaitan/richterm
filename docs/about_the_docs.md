# About this documentation

This project ships documentation as a first-class artifact, not as an afterthought.
The docs are generated with [Sphinx](https://www.sphinx-doc.org/) and [MyST](https://myst-parser.readthedocs.io/), use the
[sphinx-book-theme](https://sphinx-book-theme.readthedocs.io/), and follow [Diataxis](https://diataxis.fr/):

- tutorial content for onboarding,
- how-to guides for operation,
- reference for factual lookups,
- explanation for rationale and tradeoffs.

## Why this structure

`richterm` has both a CLI and a Sphinx extension, so the documentation needs to support several jobs at once:

- help new users run the tool quickly,
- document the directive and its configuration accurately,
- explain the development and release workflow for maintainers,
- keep rationale close to the code and workflows that implement it.

## Design decisions captured here

### Docs-as-code in the same repository

Documentation and implementation evolve together.
Any behavioral change should update docs in the same PR.

### Build should fail on docs regressions

`make docs` runs Sphinx in warning-as-error mode so broken links or directives are caught early.

### Examples should be executable

We ship [richterm](https://github.com/mgaitan/richterm) for CLI captures and
[sphinxcontrib-mermaid](https://github.com/mgaitan/sphinxcontrib-mermaid) for diagrams.

### Publishing is automated

`gh:.github/workflows/cd.yml` deploys docs to GitHub Pages:

- release/manual runs publish canonical docs,
- PRs with docs changes publish previews under
  `https://mgaitan.github.io/richterm/_preview/pr-<PR_NUMBER>/`.

For manual dispatch using `gh` CLI, authentication usually relies on {term}`GH_TOKEN`.
Workflow internals rely on {term}`GITHUB_TOKEN`.

## Configuration and glossary

Environment variables used by commands, docs examples, or workflows are documented in [Configuration](configuration.md).
When an env var appears in a chapter, reference it with `{term}` (for example {term}`PYTHONPATH`).
