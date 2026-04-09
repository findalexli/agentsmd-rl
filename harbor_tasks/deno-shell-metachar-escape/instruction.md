# Shell metacharacters not escaped in child_process args on Windows

## Problem

When using Node.js's `child_process.spawnSync()` (or `spawn()`, `exec()`, etc.) with `shell: true`, arguments containing cmd.exe metacharacters like `&`, `|`, `<`, `>`, `^`, `!`, `(`, and `)` are passed to the shell unescaped on Windows.

For example, `spawnSync('echo', ['a&b'], { shell: true })` does not output the literal string `a&b`. Instead, the shell interprets `&` as a command separator, leading to incorrect behavior — the argument gets split, a second unintended command may run, or the process produces wrong output.

The existing escaping logic in the `escapeShellArg` function in `ext/node/polyfills/internal/child_process.ts` only recognizes whitespace, double quotes, and backslashes as characters requiring quoting. It misses the full set of characters that are special to `cmd.exe`.

## Expected Behavior

Arguments containing any cmd.exe metacharacter (`&`, `|`, `<`, `>`, `^`, `!`, `(`, `)`) should be properly quoted/escaped when `shell: true` is used, so the shell treats them as literal characters rather than operators.

## Files to Look At

- `ext/node/polyfills/internal/child_process.ts` — the `escapeShellArg` function handles shell argument escaping, with separate code paths for Windows and Unix
