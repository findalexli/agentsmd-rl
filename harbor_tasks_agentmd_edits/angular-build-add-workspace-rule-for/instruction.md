# Add workspace rule for Antigravity

## Problem

The Angular repository has an `AGENTS.md` file that provides instructions for AI agents. However, Google's Antigravity tool doesn't support `AGENTS.md` directly — it uses "workspace rules" stored in `.agent/rules/`. Currently, Antigravity cannot read the Angular agent instructions.

Additionally, `AGENTS.md` is missing YAML frontmatter metadata (specifically `trigger: always_on`) that some agent frameworks require to properly load the configuration.

## Expected Behavior

1. A workspace rule symlink at `.agent/rules/agents.md` should point to `../../AGENTS.md` so Antigravity can read the same instructions
2. `AGENTS.md` should have YAML frontmatter with `trigger: always_on`
3. The new `.agent/rules/agents.md` path should be added to `.prettierignore` (it's a symlink, not a real markdown file)
4. The `.pullapprove.yml` should include `.agent/**/{*,.*}` in its file globs so the rules directory is covered by the appropriate review group

## Files to Look At

- `AGENTS.md` — main agent instructions file (needs frontmatter added)
- `.agent/rules/agents.md` — new symlink to create
- `.prettierignore` — needs new ignore entry
- `.pullapprove.yml` — needs new glob pattern
