# fix: Auto-fix SKILL.md validation errors (1 fixed)

Source: [aiskillstore/marketplace#644](https://github.com/aiskillstore/marketplace/pull/644)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/google-labs-code/react-components/SKILL.md`

## What to add / change

## Summary

AI-powered auto-fix for SKILL.md validation errors.

| Metric | Value |
|--------|-------|
| Files Fixed | 1 |
| Empty Skills Deleted | 0 |
| Triggered By | push |

### Fixes Applied
- Added missing YAML frontmatter
- Fixed `name` field format (lowercase alphanumeric with hyphens)
- Added missing `description` field
- Truncated overly long descriptions
- **Deleted empty skill directories** (unfixable)

### After Merge
The `sync-to-supabase.yml` workflow will automatically update the database.

---
*Automated fix by validate-marketplace.yml*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
