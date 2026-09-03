# diagrams Maintainer Guide

## Purpose And Boundaries

This repository owns DiagramFlow's public `diagrams` Python distribution. It
preserves the `diagrams` package name, provider modules, resource layout, and
rendering behavior while using an independent DiagramFlow release lifecycle.

Keep the library general purpose. Do not import DiagramFlow application code,
publish to PyPI or private indexes, or configure automatic synchronization with
`mingrammer/diagrams`.

## Required Context

Start at [Documentation](/diagrams/docs/README.md), then use:

- [Maintenance Contract](/diagrams/docs/maintenance.md) for compatibility and release policy.
- [Upstream Provenance](/diagrams/UPSTREAM.md) for snapshot history and attribution.
- [Releases](/diagrams/docs/releases/README.md) for release evidence.
- [Migrations](/diagrams/docs/migrations/README.md) for compatibility-impacting upgrades.

## Commands

Graphviz must be installed and available on `PATH`.

```bash
uv sync --all-groups
uv run pytest
```

## Compatibility And Release Guardrails

- Preserve public APIs, provider modules, resource paths, and rendering output
  unless a compatibility-reviewed release intentionally changes them.
- Use Semantic Versioning. Release tags are immutable; never move or replace a
  published `v*` tag.
- Runtime consumers install from a Git tag and frozen lockfile, not PyPI.
- Python 3.11 tests and compatibility gates are the release baseline even when
  package metadata supports a wider interpreter range.
- Patch security issues in this repository, run the full compatibility suite,
  and publish a new semantic version. Do not assume upstream will apply fixes.

## Verification

Inspect affected provider imports, resources, tests, release docs, and consumers
before changing compatibility behavior. Run focused tests first, then
`uv run pytest`. Update maintenance, migration, release, and provenance docs
only when their owned contract changes; preserve unrelated work.
