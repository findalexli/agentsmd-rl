# fix: replace unsupported --version flag with -help in codemap setup skill

Source: [NeoLabHQ/context-engineering-kit#63](https://github.com/NeoLabHQ/context-engineering-kit/pull/63)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/mcp/skills/setup-codemap-cli/SKILL.md`

## What to add / change

## Summary

- Replace `codemap --version` with `codemap -help` for installation detection (step 2)
- Remove `codemap --version` from verification step (step 5), keep only `codemap .`

## Problem

The `mcp:setup-codemap-cli` skill uses `codemap --version` to check if codemap is installed and to verify the installation. However, codemap is a Go binary using Go's `flag` package and does **not** implement a `--version` flag. This causes an exit code 2 error:

```
Error: Exit code 2
flag provided but not defined: -version
```

The setup still works because the agent sees the usage output and infers codemap is installed, but it produces a confusing error message.

## Fix

- **Step 2** (detection): `codemap --version` → `codemap -help`
- **Step 5** (verification): removed `codemap --version`, kept `codemap .` which is a reliable functional test

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
