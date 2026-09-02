# Diagrams Documentation

## Purpose

This is the maintainer router for DiagramFlow's independently governed public
`diagrams` distribution. The repository is a shared Python library, not a
DiagramFlow backend service, so it does not own service API, database, event,
or deployment-runtime documentation.

## Current Contracts

- [Public package overview](/README.md) — installation, supported public use,
  and package entry points.
- [Maintenance](/docs/maintenance.md) — compatibility, release, security, and
  runtime-consumer policy.
- [Development](/DEVELOPMENT.md) — local development environments and legacy
  contributor commands.
- [Contributing](/CONTRIBUTING.md) — contribution workflow.
- [Agent guide](/AGENTS.md) — task routing, boundaries, commands, and security
  constraints.

## Lifecycle And Provenance

- [Upstream provenance](/UPSTREAM.md) — immutable source snapshot and ownership
  transfer boundary.
- [Release history](/CHANGELOG.md) and [release index](/docs/releases/README.md)
  — historical shipped evidence; these do not replace current contracts.
- [Migration index](/docs/migrations/README.md) — compatibility-impacting
  consumer guidance between DiagramFlow releases.
- [Decision index](/docs/decisions/README.md) — active repository-local
  architectural decisions, when any are introduced.

## Verification

Use Python 3.11 with Graphviz available on `PATH` for the release gate:

```bash
uv sync --all-groups --frozen
uv run pytest
```

The compatibility workflow additionally renders a fixed corpus with upstream
`diagrams==0.25.1` and compares it with the candidate package.
