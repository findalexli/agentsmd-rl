# Set up Claude Code configuration with sane defaults

## Problem

The Payload CMS repository is missing Claude Code integration configuration. There are no post-edit hooks to automatically format files after edits, no permissions presets to reduce prompts for common read-only commands, and the `CLAUDE.md` documentation is incomplete and inconsistent.

Specifically:
- No `.claude/hooks/` directory or formatting hooks exist — files edited by Claude Code don't get auto-formatted
- No `.claude/settings.json` exists — every git/pnpm command triggers a permission prompt
- `CLAUDE.md` is missing documentation for some packages (`kv-redis`, R2 storage adapter)
- `CLAUDE.md` has no Quick Start section for new contributors
- pnpm commands in `CLAUDE.md` use inconsistent formats — some use bare `pnpm build` while the monorepo's permission rules require `pnpm run build`
- No guidance about running Turbo commands through pnpm rather than directly

## Expected Behavior

### 1. Post-edit hook (`.claude/hooks/post-edit.sh`)

Create a bash script at `.claude/hooks/post-edit.sh` that:
- Reads JSON from stdin (e.g. `{"tool_input": {"file_path": "/path/to/file"}}`)
- Exits 0 gracefully when `file_path` is null, missing, or the JSON is empty
- Uses a `case`/`esac` construct to route files by extension/type to the correct formatter:
  - `*.ts` files → run `eslint --fix`
  - `*.md` files → run `prettier --write`
  - `package.json` → run `sort-package-json`
  - all other files → run `prettier --write`

The script must contain the literal strings: `case`, `esac`, `*.ts`, `*.md`, `package.json`, `prettier`, `eslint`.

### 2. Settings (`.claude/settings.json`)

Create `.claude/settings.json` with this schema:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "command": "bash .claude/hooks/post-edit.sh"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "<list of at least 10 commands>",
      "pnpm run <cmd>",
      "pnpm turbo <cmd>",
      "git log",
      "git diff"
    ]
  }
}
```

Key requirements:
- `hooks.PostToolUse` must be an array with at least one entry
- The entry's `matcher` field must contain both the strings "Edit" and "Write" (e.g. `"Edit|Write"`)
- The `hooks` array within that entry must contain an object with a `command` field referencing "post-edit"
- `permissions.allow` must be a list with **at least 10 entries**
- The allowlist must include the exact substrings `pnpm run`, `pnpm turbo`, and either `git log` or `git diff`

### 3. CLAUDE.md updates

Update `CLAUDE.md` to add:

1. **Missing packages in key directories**: Add `kv-redis` to the packages listing
2. **R2 storage adapter**: Add `R2` alongside the storage adapters entry (e.g. `storage-* adapters (S3, R2, etc.)`)
3. **Quick Start section**: Add a `## Quick Start` (or `### Quick Start`) section that includes at least one `pnpm` command
4. **Standardized pnpm commands**: All `pnpm build`, `pnpm dev`, `pnpm test`, and `pnpm lint` commands must use the `pnpm run` prefix (i.e. `pnpm run build` not `pnpm build`). At least 3 such commands must use the prefix.
5. **Turbo guidance**: Include the phrase `pnpm turbo` and a warning that turbo must not be run directly (e.g. "use `pnpm turbo` not bare `turbo`")

## Files to Create/Modify

- `.claude/hooks/post-edit.sh` — new hook script for auto-formatting
- `.claude/settings.json` — new settings with hooks and permissions
- `CLAUDE.md` — existing documentation that needs updates
