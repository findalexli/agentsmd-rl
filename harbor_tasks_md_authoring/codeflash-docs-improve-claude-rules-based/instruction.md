# docs: improve Claude rules based on eval results

Source: [codeflash-ai/codeflash#1851](https://github.com/codeflash-ai/codeflash/pull/1851)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/code-style.md`
- `.claude/rules/git.md`
- `.claude/rules/testing.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Strengthened docstring, verification, tmp_path, and .resolve() rules based on eval runs comparing with-rules vs without-rules behavior
- Expanded git commit/PR conventions and bug fix workflow instructions
- Added type annotation and verification rules that were missing

## Eval findings that drove changes
- **Docstrings**: Both with/without rules added docstrings — stronger phrasing needed
- **tmp_path**: With-rules agent copied old `tempfile.mkdtemp()` from existing code — explicitly banned alternatives
- **`.resolve()`**: Never followed — added concrete example
- **`prek`**: Baseline ran ruff/mypy separately — clarified prek is the single command

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
