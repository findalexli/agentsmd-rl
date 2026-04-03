# Add watch, tag, and description commands to ClickUp skill

## Problem

The ClickUp CLI skill in `.claude/skills/clickup/` is missing several useful task management commands:

1. **watch** — There's no way to notify a user about a task. The ClickUp API v2 doesn't support adding watchers programmatically, so this needs a workaround (e.g., posting an @mention comment instead).

2. **tag** — There's no way to add tags to tasks. ClickUp's API supports adding tags via `POST /task/{id}/tag/{tag_name}`.

3. **description** — There's no way to update a task's description from the CLI. ClickUp supports a `markdown_description` field on tasks for proper markdown rendering.

Each new command needs:
- An API function in `api/tasks.mjs`
- A command handler in `query.mjs` (with proper argument validation and error messages)
- The command listed in the help/usage text

Also note: the existing `create` command currently uses `options.description` when passing a description to new tasks, but ClickUp's API uses `markdown_description` for proper markdown rendering. This should be fixed.

## Expected Behavior

- `node query.mjs watch <task> <user>` notifies the user about the task (since direct watcher API isn't available, use an alternative like @mention comments)
- `node query.mjs tag <task> "tag_name"` adds a tag to the task
- `node query.mjs description <task> "text"` updates the task description with markdown support
- Each command shows a helpful error when required arguments are missing
- All commands appear in the CLI help text

After implementing the code changes, update the skill's documentation (`.claude/skills/clickup/SKILL.md`) to document the new commands — add them to the commands table, include usage examples, and update any relevant sections that describe what the skill can do.

## Files to Look At

- `.claude/skills/clickup/api/tasks.mjs` — API functions for task operations
- `.claude/skills/clickup/query.mjs` — CLI command dispatcher and argument handling
- `.claude/skills/clickup/SKILL.md` — Skill documentation with command reference and examples
- `.claude/skills/clickup/api/client.mjs` — Shared API request helper (for reference)
