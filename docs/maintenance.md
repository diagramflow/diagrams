# Maintenance

This repository is DiagramFlow's independent, public distribution of the
`diagrams` Python package.

## Local Setup

Requirements:

- Python 3.9 through 3.13 for CI compatibility.
- Python 3.11 for release-gate verification.
- Graphviz on `PATH`.
- `uv` for dependency resolution and test execution.

Commands:

```bash
uv sync --all-groups
uv run pytest
```

## Compatibility Contract

The `v1.0.0` release is a compatibility release based on upstream
`mingrammer/diagrams v0.25.1` at commit
`dd0763d939f377c99898951a489e813c0360cd4a`.

Maintain compatibility for:

- Python package name and namespace: `diagrams`.
- Public modules and provider classes.
- Packaged resources under `resources/`.
- Graphviz-facing rendering behavior.
- Runtime dependency bounds unless a reviewed release changes them.

## Release Policy

- Use Semantic Versioning.
- Create immutable annotated tags such as `v1.0.0`.
- Do not publish wheels or source distributions to PyPI.
- Do not move existing release tags. Ship fixes as new versions.
- Do not configure automatic upstream synchronization.

## Security And Operations

DiagramFlow owns security maintenance after the snapshot. Treat dependency,
Python, Graphviz, and packaged-resource issues as DiagramFlow-owned issues even
when the original code came from upstream.

Runtime services should consume this repository from a public Git tag with a
frozen lockfile. A failed Git fetch during a new build should fail the build,
not fall back to PyPI.

## Consumer Compatibility

- Diagram Service may emit only public `diagrams` imports supported by the
  selected release.
- Generate Service resolves the public Git tag to an exact commit in `uv.lock`,
  builds it into the container image, and has no runtime dependency on GitHub.
- Consumer HTTP contracts, `.df` conversion ownership, and subprocess isolation
  remain outside this library.
- Verify the library import/resource corpus, Diagram Service node-registry
  imports, and Generate Service PNG/JPG/SVG execution before adopting a new
  release.

If a build cannot resolve the immutable Git source, stop the build and retain
the last verified container image. If a rendering regression appears after
deployment, roll back the consumer image and release a new semantic version;
never move an existing tag.
