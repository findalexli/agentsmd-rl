# docs(lark-doc): replace literal \n examples with real-newline forms

Source: [larksuite/cli#602](https://github.com/larksuite/cli/pull/602)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-doc/references/lark-doc-create.md`
- `skills/lark-doc/references/lark-doc-update.md`

## What to add / change

## Summary

Fixes #580 — the official `docs +create` / `docs +update` skill examples teach the pattern:

```bash
lark-cli docs +create --title "项目计划" --markdown "## 目标\n\n- 目标 1\n- 目标 2"
```

Inside bash double quotes, `\n` is a **literal backslash + n** (two characters), not a newline. `lark-cli` forwards the value byte-for-byte to MCP, so the resulting Feishu document ends up containing the literal text `\n\n` everywhere instead of paragraph breaks. Agents and users copy-pasting the examples reliably produce broken docs.

## Verified locally

Reproduced against `lark-cli v1.0.14-8-g9017741` on macOS, bash:

- `--dry-run` payload shows `"content": "## A\\n\\n- x\\n- y"` (literal backslash-n passed through to the API)
- Creating a real doc with the buggy pattern yields `<title>Untitled</title><h2>A\n\n- x\n- y</h2>` — the whole markdown structure collapses into a single H2 with visible `\n\n` text

## Scope

**Documentation-only fix**, per the reporter's Option 1. CLI behavior is intentionally unchanged — byte-for-byte forwarding matches standard shell semantics, and auto-interpreting `\n` (Option 2) would be a breaking change.

## Changes

Two skill files, 9 buggy example occurrences plus 1 single-quoted variant:

### `skills/lark-doc/references/lark-doc-create.md`

- Fix 3 `"...\n..."` examples in the `## 命令` block (lines 15, 18 previously)
- Fix 1 `"...\n..."` example in `## 示例 1` (line 119 previously)
- Fix 1 `'...\n...'` single-quoted example

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
