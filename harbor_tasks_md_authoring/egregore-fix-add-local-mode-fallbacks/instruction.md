# fix: add local mode fallbacks for /todo, /issue, and /add commands

Source: [egregore-labs/egregore#1](https://github.com/egregore-labs/egregore/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add/SKILL.md`
- `.claude/skills/issue/SKILL.md`
- `.claude/skills/todo/SKILL.md`

## What to add / change

These three commands were the only graph-dependent commands missing local mode handling. All other commands (16 total) gracefully degrade to filesystem-backed operations in local mode.

### Changes

- **`/todo`** (+52 lines): YAML-backed storage in `memory/todos/{person}.md`. All routes (add, list, done, cancel, check) work identically. Quest matching reads from `memory/quests/` directory. CheckIn history not persisted (acceptable trade-off).
- **`/issue`** (+17 lines): Filesystem-only create/list/close/search via `memory/knowledge/issues/`. Skip graph node creation and notifications.
- **`/add`** (+18 lines): Skip graph Artifact node creation. Artifact file in `memory/artifacts/` is source of truth. Quest matching reads from `memory/quests/` files.

### Pattern

Follows the exact same local mode gate pattern established by:
- `handoff.md:18`, `reflect.md:34`, `quest.md:49`, `ask.md:42`
- `archive.md:31`, `summon.md:19`, `activity.md`, `dashboard.md`

### Testing

Verified in a local-mode Egregore instance. Before this change, all three commands either returned empty results or showed "Graph offline" with no fallback.

---
Contributed via `/contribute` from an Egregore instance.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
