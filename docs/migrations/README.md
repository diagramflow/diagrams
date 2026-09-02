# Migration Guide Index

## Purpose

This index routes consumers to compatibility-impacting changes between
DiagramFlow-owned `diagrams` releases.

## Current Guidance

No DiagramFlow-to-DiagramFlow migration is required for the initial `v1.0.0`
release. It intentionally preserves the public package name, module layout,
provider classes, resources, and rendering behavior of upstream `v0.25.1`.

Before a future incompatible release, add a versioned migration guide here and
link it from [Maintenance](/docs/maintenance.md), [Release history](/CHANGELOG.md),
and the affected current contract. Do not use release notes as the only owner
of a current consumer requirement.
