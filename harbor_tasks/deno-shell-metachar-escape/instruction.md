# Shell metacharacters not escaped in child_process args on Windows

## Problem

When using Node.js's `child_process.spawnSync()` (or `spawn()`, `exec()`, etc.) with `shell: true`, arguments containing cmd.exe metacharacters are passed to the shell unescaped on Windows.

For example, `spawnSync('echo', ['a&b'], { shell: true })` does not output the literal string `a&b`. Instead, the shell interprets `&` as a command separator, leading to incorrect behavior — the argument gets split, a second unintended command may run, or the process produces wrong output.

The bug is in the file `ext/node/polyfills/internal/child_process.ts`, in the `escapeShellArg` function. The shell argument escaping logic on the Windows code path fails to recognize the full set of characters that are special to cmd.exe.

## Expected Behavior

Arguments containing any of the following cmd.exe metacharacters must be properly quoted/escaped when `shell: true` is used, so the shell treats them as literal characters rather than operators:

- `&` (command separator)
- `|` (pipe)
- `<` (input redirect)
- `>` (output redirect)
- `^` (escape character)
- `!` (delayed expansion)
- `(` and `)` (grouping)

Example arguments that must be escaped: `a&b`, `x|y`, `foo&bar|baz`, `a<b`, `c>d`, `e^f`, `x<y>z^w`, `hello!`, `(test)`, `a(b)c`, `!done`.

Plain alphanumeric arguments (e.g., `hello`, `foo123`, `simple.txt`, `path/to/file`, `my-flag`) must pass through unchanged — they should not be unnecessarily quoted.

Arguments containing characters that are already properly handled (spaces, double quotes, backslashes) must continue to be escaped correctly after the fix.

## Constraints

- The fix should only affect the Windows code path.
- After fixing, `deno lint` and `deno fmt --check` must pass on the modified file.
- Existing child_process spec tests in the repo must continue to pass.
- The relevant spec test is at `tests/specs/node/child_process_shell_escape/main.ts`.
