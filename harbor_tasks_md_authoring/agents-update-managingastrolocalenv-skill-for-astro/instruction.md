# Update managing-astro-local-env skill for Astro CLI v1.40

Source: [astronomer/agents#180](https://github.com/astronomer/agents/pull/180)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/managing-astro-local-env/SKILL.md`

## What to add / change

## Summary

- Add **standalone mode** section — Docker-free local dev with `astro dev start --standalone`, covering start/stop/kill/restart, flags, requirements, and state locations
- Add **reverse proxy** section — multi-project local dev with `<project>.localhost:6563` hostnames, proxy status/stop commands, and config
- Add **querying the Airflow API** section — `astro api airflow` with operation ID examples for DAGs, DAG runs, task instances, logs, connections, variables, and jq filtering
- Update existing sections with standalone mode notes (logs, CLI commands, troubleshooting)
- Rename "Access Container Shell" to "Run Airflow CLI Commands" (works in both modes)

All flags and operation IDs verified against `astro --help` and `astro api airflow describe` output from Astro CLI v1.40.1.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
