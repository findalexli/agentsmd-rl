#!/usr/bin/env bash
set -euo pipefail

cd /workspace/todoist-cli

# Idempotency guard
if grep -qF "7. **Bounded, high-signal responses** \u2014 List commands use `paginate()` from `src" ".agents/skills/add-command/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/add-command/SKILL.md b/.agents/skills/add-command/SKILL.md
@@ -31,7 +31,25 @@ If the new command uses a **read-only** SDK method (e.g., `getXxx`, `listXxx`),
 - **Read-only methods** (fetch/list/view): add to `KNOWN_SAFE_API_METHODS`
 - **Mutating methods** (add/update/delete/archive/move): do NOT add — they are blocked by default, which is the correct behavior
 
-## 4. Command Implementation (`src/commands/<entity>/`)
+## 4. Agent-Friendly Design Checklist
+
+Every new command should satisfy these properties. They ensure the CLI works well for both humans and AI agents. See [7 Principles for Agent-Friendly CLIs](https://trevinsays.com/p/7-principles-for-agent-friendly-clis) for background.
+
+1. **Non-interactive by default** — All input via flags, positional args, or `--stdin`. Never use `readline`, `prompt()`, or block waiting for TTY input. When a required argument is missing, call `cmd.help()` and return — don't prompt.
+
+2. **Structured, parseable output** — Data commands must support `--json` (and `--ndjson` for lists). Results go to stdout, diagnostics to stderr. Spinners auto-suppress when `!process.stdout.isTTY` (see `src/lib/spinner.ts`). Exit code 0 on success, non-zero on failure.
+
+3. **Fail fast with actionable errors** — Use `CliError` with a specific error code, a message naming the exact problem, and hints that include correct invocation syntax, valid values, or example commands. Validate all inputs before making API calls.
+
+4. **Safe retries and explicit mutation boundaries** — Mutating commands support `--dry-run`. Destructive + irreversible commands require `--yes`. Create commands return the entity ID (use `isQuiet()` for bare ID output for scripting, e.g. `id=$(td task add "Buy milk" -q)`).
+
+5. **Progressive help discovery** — Parent command groups include `.addHelpText('after', ...)` with 2–3 concrete examples. Every `.description()` is a clear one-line purpose statement. When a required positional arg is missing, show help via `cmd.help()`.
+
+6. **Composable and predictable structure** — Use consistent subcommand verbs (`list`/`view`/`create`/`update`/`delete`/`browse`). Use consistent flag names across entities (`--project <ref>`, `--json`, `--dry-run`, `--yes`, `--limit`, `--cursor`, `--all`). Support `--stdin` for text content where applicable (see `readStdin()` in `src/lib/stdin.ts`).
+
+7. **Bounded, high-signal responses** — List commands use `paginate()` from `src/lib/pagination.ts` with `--limit <n>`, `--cursor`, and `--all` flags. When results are truncated, `formatNextCursorFooter()` tells the user how to fetch more. JSON output uses `formatJson()` or `formatPaginatedJson()` to return essential fields by default, passing the `--full` flag for complete output.
+
+## 5. Command Implementation (`src/commands/<entity>/`)
 
 Commands with multiple subcommands use a folder-based structure:
 
@@ -57,13 +75,17 @@ Single-subcommand commands (e.g., `add.ts`, `today.ts`) remain as flat files.
 
 ### Flag conventions
 
-| Command type                   | Flags                                    |
-| ------------------------------ | ---------------------------------------- |
-| Read-only                      | `--json` (and `--ndjson` for lists)      |
-| Mutating (returns entity)      | `--json` (use `formatJson`), `--dry-run` |
-| Mutating (no return)           | `--dry-run`                              |
-| Destructive + irreversible     | `--yes`, `--dry-run`                     |
-| Reversible (archive/unarchive) | `--dry-run` (no `--yes`)                 |
+| Command type                   | Flags                                                    |
+| ------------------------------ | -------------------------------------------------------- |
+| Read-only                      | `--json` (and `--ndjson` for lists)                      |
+| Mutating (returns entity)      | `--json` (use `formatJson`), `--dry-run`                 |
+| Mutating (no return)           | `--dry-run`                                              |
+| Destructive + irreversible     | `--yes`, `--dry-run`                                     |
+| Reversible (archive/unarchive) | `--dry-run` (no `--yes`)                                 |
+| List (paginated)               | `--limit <n>`, `--cursor`, `--all`, `--json`, `--ndjson` |
+| List (non-paginated)           | `--json`, `--ndjson`                                     |
+
+The `--quiet` / `-q` flag suppresses success messages on mutations. Create commands in quiet mode print only the bare entity ID for scripting (e.g., `id=$(td task add "Buy milk" -q)`).
 
 ### Error handling
 
@@ -77,6 +99,12 @@ throw new CliError('ERROR_CODE', 'User-facing message', ['Optional hint'])
 
 When adding a new error code, add it to the `ErrorCode` type in `src/lib/errors.ts` under the appropriate category. The type provides intellisense for known codes while accepting any string for dynamic codes.
 
+To make errors actionable for agents:
+
+- The `message` must name the specific problem (not generic "invalid input")
+- The `hints` array should include at least one of: correct invocation syntax, valid values, or a working example command
+- Validate all flag constraints and input early — before any API calls. If flags conflict, throw `CliError('CONFLICTING_OPTIONS', ...)` immediately
+
 ### ID resolution
 
 - `resolveXxxRef(api, ref)` — when the user knows the entity by name (projects, tasks, labels). Add new wrappers in `refs.ts` — `resolveRef` is private.
@@ -102,7 +130,13 @@ const myCmd = parent
 
 The variable assignment (`const myCmd = ...`) is needed so the `.action()` callback can call `myCmd.help()` when the argument is missing.
 
-## 5. Accessibility (`src/lib/output.ts`)
+Help text quality:
+
+- Parent command groups (the `registerXxxCommand` function) should include `.addHelpText('after', ...)` with 2–3 concrete invocation examples
+- Every `.description()` string should be a clear one-line purpose — agents read this to decide which subcommand to call
+- The `if (!ref) { cmd.help(); return }` pattern ensures the command never blocks when a required argument is missing
+
+## 6. Accessibility (`src/lib/output.ts`)
 
 The CLI supports accessible mode via `isAccessible()` (checks `TD_ACCESSIBLE=1` or `--accessible` flag). When adding output that uses color or visual elements, consider whether information is conveyed **only** by color or decoration.
 
@@ -138,7 +172,7 @@ if (isAccessible()) {
 
 If adding a new shared formatter to `output.ts`, use `Record<ExactType, ...>` rather than `Record<string, ...>` so the compiler catches missing variants.
 
-## 6. Tests (`src/__tests__/<entity>.test.ts`)
+## 7. Tests (`src/__tests__/<entity>.test.ts`)
 
 Follow the existing pattern: mock `getApi`, use `program.parseAsync()`.
 
@@ -149,7 +183,7 @@ Always test:
 - `--dry-run` for mutating commands (API method should NOT be called, preview text shown)
 - `--json` output where applicable
 
-## 7. Skill Content (`src/lib/skills/content.ts`)
+## 8. Skill Content (`src/lib/skills/content.ts`)
 
 Update `SKILL_CONTENT` with examples for the new command. Update relevant sections:
 
@@ -158,7 +192,7 @@ Update `SKILL_CONTENT` with examples for the new command. Update relevant sectio
 - Mutating `--json` list if the command returns an entity
 - `--dry-run` list if applicable
 
-## 8. Sync Skill File
+## 9. Sync Skill File
 
 After all code changes are complete:
 
@@ -168,7 +202,7 @@ npm run sync:skill
 
 This builds the project and regenerates `skills/todoist-cli/SKILL.md` from the compiled skill content. The regenerated file must be committed. CI will fail (`npm run check:skill-sync`) if it is out of sync.
 
-## 9. Verify
+## 10. Verify
 
 ```bash
 npm run type-check
PATCH

echo "Gold patch applied."
