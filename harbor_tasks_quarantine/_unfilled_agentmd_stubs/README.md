# Unfilled agentmd_edits Template Stubs (2026-04-24)

These 6086 directories were created by an early scout pass that copied the task
template into a directory per scouted PR but never actually scaffolded them.
Every `instruction.md` contains literal `{{TASK_TITLE}}` / `{{TARGET_FILE}}` /
`TODO: Describe` placeholders.

They are not real tasks. They have:
- No filled-in `instruction.md` (template only)
- No `solution/solve.sh` (template only — `{{PATCH_CONTENT}}` placeholder)
- No `environment/Dockerfile` (template only — `{{OWNER}}` / `{{REPO}}` placeholders)
- No `tests/test_outputs.py` (template only)
- No `status.json` (never validated)

## Why quarantined, not deleted

Preserves the directory names (which encode PR slugs from the scout pass), so
they remain re-scaffoldable by feeding the names back through `/scaffold-task`
or `gemini_rubric_constructor.py`.

## Recovery

To reinstate a single stub for re-scaffolding:

```bash
mv harbor_tasks_quarantine/_unfilled_agentmd_stubs/<task-name> harbor_tasks_agentmd_edits/
# Then re-scaffold from the source PR
```

But the cleaner path is to discard these directories entirely and rescout the
underlying repos for fresh PRs — most of these slugs are stale (>3 weeks old).

## What's left in `harbor_tasks_agentmd_edits/`

After this quarantine: **81 real tasks** (63 validated + 18 partial scaffolds).
