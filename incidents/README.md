# Incidents

This folder contains controlled data incident definitions and expected failure notes.

- `incident_catalog.yml` is the YAML registry for all benchmark incidents.
- `expected_failures/` contains short representative validation failures.
- `.state/` is created locally when incidents are injected and stores reset backups.

Use `make list-incidents`, `make break-incident-01`, and `make reset-incident-01` from the repository root. Full usage and learning notes are in `docs/incidents.md`.
