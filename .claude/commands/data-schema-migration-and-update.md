---
name: data-schema-migration-and-update
description: Workflow command scaffold for data-schema-migration-and-update in hot-trend-root.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /data-schema-migration-and-update

Use this workflow when working on **data-schema-migration-and-update** in `hot-trend-root`.

## Goal

Migrates or updates the core data schema and migrates/cleans up data files to match new schema requirements.

## Common Files

- `project/codingplan-saver/data/SCHEMA.md`
- `project/codingplan-saver/data/site.json`
- `project/codingplan-saver/data/vendors.json`
- `project/codingplan-saver/data/plans.json`
- `project/codingplan-saver/data/changes.json`
- `dist/codingplan-saver.html`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit or create project/codingplan-saver/data/SCHEMA.md to define schema changes.
- Update or migrate JSON data files: site.json, vendors.json, plans.json, changes.json.
- If needed, write migration scripts or perform manual data transformation.
- Clean up or remove deprecated data fields and files.
- Update documentation (e.g., reference/data-map.md) to reflect new schema.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.