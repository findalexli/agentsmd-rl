# docs(lark-drive): add missing import command examples

Source: [larksuite/cli#669](https://github.com/larksuite/cli/pull/669)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-drive/references/lark-drive-import.md`

## What to add / change

## Summary
- Adds example commands to the "命令" section of `skills/lark-drive/references/lark-drive-import.md` for file types that are declared in the supported-conversions table but had no example.
- New examples cover: `.docx` / `.doc` (Office Word), `.txt`, `.html`, `.xls -> sheet`, and `.csv -> sheet`.
- Documentation only — no behavior changes.

## Test plan
All six examples were executed end-to-end against the real Lark Import API with `--as user`. Each produced an `ok: true` response with a valid online doc URL.

| Local file | `--type` | Result |
|------------|----------|--------|
| `.docx` | `docx` | ✅ |
| `.doc` | `docx` | ✅ |
| `.txt` | `docx` | ✅ |
| `.html` | `docx` | ✅ |
| `.xls` | `sheet` | ✅ |
| `.csv` | `sheet` | ✅ |

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
