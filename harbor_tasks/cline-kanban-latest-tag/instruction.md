# Task: Fix kanban command to use latest version

## Problem

When users run the `cline kanban` command or use the `--kanban` option, the CLI spawns `npx -y kanban` which may use a cached version of the package from the local npm cache. This means users might not get the most recent kanban release; they could be running an older version that's cached locally instead of fetching the newest release from the registry.

## How to Fix It

The code needs to be updated so that npx always fetches the newest version from the registry rather than potentially using a stale cached version. The fix involves changing several string literals in the CLI to append `@latest` to the kanban package reference.

You will need to modify:

1. **Spawn call in `runKanbanAlias` function** — The npx spawn call currently uses `"kanban"` and must be updated to use `"kanban@latest"` in the same argument position. The function is in `cli/src/index.ts`.

2. **Error message** — The warning message that prints when the kanban process fails to start currently references the old command string and must be updated to reference the new command string.

3. **Command description** — The `.command("kanban").description()` call must be updated to reference the new command string.

4. **Option description** — The `.option("--kanban", ...)` call must be updated to reference the new command string.

5. **Test file** — The test file `cli/src/index.test.ts` must also be updated so that its descriptions match the implementation.

After the fix, when users run `cline kanban`, the CLI will always fetch the most recent version from the registry.

## Constraints

- Only modify string literals related to the kanban command
- Do not change any logic or behavior beyond the package reference
- Ensure test descriptions match the implementation
