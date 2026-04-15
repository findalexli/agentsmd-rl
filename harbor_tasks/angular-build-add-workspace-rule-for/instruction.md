# Add workspace rule for Antigravity

## Problem

The Angular repository uses an `AGENTS.md` file to provide instructions for AI agents. However, Google's Antigravity tool does not read `AGENTS.md` directly - it expects to find "workspace rules" in the `.agent/rules/` directory.

Currently:
- The `.agent/rules/agents.md` path does not exist (Antigravity cannot locate agent instructions)
- `AGENTS.md` lacks YAML frontmatter metadata required by some agent frameworks to properly load the configuration (specifically missing `trigger: always_on`)
- `.prettierignore` does not exclude `.agent/rules/agents.md`
- `.pullapprove.yml` does not include the glob pattern `.agent/**/{*,.*}` for review coverage

## Expected Behavior

After the fix, the repository should satisfy these requirements:

1. **Workspace rule accessible**: Antigravity should be able to read agent instructions from `.agent/rules/agents.md`. The content at that path should match the existing `AGENTS.md` file.

2. **Frontmatter present**: `AGENTS.md` should have YAML frontmatter containing `trigger: always_on`.

3. **Prettier ignore configured**: `.prettierignore` should contain an entry for `.agent/rules/agents.md`.

4. **PullApprove coverage**: `.pullapprove.yml` should include the glob pattern `.agent/**/{*,.*}` in its file patterns.

5. **Existing content preserved**: `AGENTS.md` should retain its existing documentation sections including `## Environment` and references to `pnpm`.

## Files to Look At

- `AGENTS.md` - main agent instructions file
- `.agent/rules/` - workspace rules directory for Antigravity
- `.prettierignore` - ignore patterns for Prettier formatting
- `.pullapprove.yml` - review group configuration
