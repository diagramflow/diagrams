# AGENTS

This repository contains DiagramFlow's public `diagrams` distribution. It keeps
the package name and Python namespace `diagrams` while using an independent
DiagramFlow release lifecycle.

## Scope

- Preserve the public API, provider modules, resource layout, and rendering
  behavior unless a new compatibility-reviewed release intentionally changes
  them.
- Keep the library general purpose. Do not import DiagramFlow application code.
- Do not publish this package to PyPI or private package indexes.
- Do not configure automatic synchronization with `mingrammer/diagrams`.

## Development

Install dependencies and run tests with uv:

```bash
uv sync --all-groups
uv run pytest
```

Graphviz must be installed and available on `PATH` for rendering tests.

## Release Policy

- Use Semantic Versioning.
- The Python 3.11 test and compatibility gates are the release baseline.
- Release tags are immutable. Never move or replace a published `v*` tag.
- Fixes after `v1.0.0` must use a new version and a new tag.
- Runtime consumers should install from a Git tag and frozen lockfile, not PyPI.

## Security

DiagramFlow owns security triage for this distribution after the snapshot. Patch
security issues in this repository, run the full compatibility suite, and cut a
new semantic version. Do not assume upstream will provide or apply fixes here.
