# refactor: rename skills for clarity

Source: [astronomer/agents#14](https://github.com/astronomer/agents/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `shared-skills/airflow-2-to-3-migration/SKILL.md`
- `shared-skills/check-freshness/SKILL.md`
- `shared-skills/debug-dag/SKILL.md`
- `shared-skills/discover-data/SKILL.md`
- `shared-skills/downstream-lineage/SKILL.md`
- `shared-skills/profile-table/SKILL.md`
- `shared-skills/upstream-lineage/SKILL.md`

## What to add / change

## Summary
- Renamed 6 skills to be more descriptive and action-oriented
- Fixed folder/frontmatter mismatch for airflow migration skill

| Old Name | New Name |
|----------|----------|
| `airflow-migration` | `airflow-2-to-3-migration` |
| `diagnose` | `debug-dag` |
| `explore` | `discover-data` |
| `freshness` | `check-freshness` |
| `impacts` | `downstream-lineage` |
| `profile` | `profile-table` |
| `sources` | `upstream-lineage` |

## Test plan
- [ ] Verify skills are discoverable with new names
- [ ] Reinstall plugin and confirm skills load correctly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
