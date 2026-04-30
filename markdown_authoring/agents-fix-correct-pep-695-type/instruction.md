# fix: correct PEP 695 type statement Python version (3.10 -> 3.12)

Source: [wshobson/agents#463](https://github.com/wshobson/agents/pull/463)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/python-development/skills/python-type-safety/SKILL.md`

## What to add / change

## TL;DR

Fix incorrect Python version for PEP 695 `type` statement syntax in the python-type-safety skill. The text said Python 3.10; the correct version is Python 3.12.

## What changed

File: `plugins/python-development/skills/python-type-safety/SKILL.md`

The note at line 334 previously stated:

> The `type` statement was introduced in Python 3.10 for simple aliases.

This is incorrect. PEP 695 (Type Parameter Syntax) targets Python 3.12, as stated in the PEP metadata (`Python-Version: 3.12`). Both simple aliases (`type X = str`) and generic aliases (`type X[T] = list[T]`) require Python 3.12+. Using this syntax on Python 3.10 or 3.11 raises `SyntaxError`.

The fix updates the note and code comments to accurately reflect Python 3.12, and clarifies the pre-3.12 alternative (`TypeAlias` from PEP 613, available since Python 3.10).

## References

- PEP 695 metadata: `Python-Version: 3.12` -- https://peps.python.org/pep-0695/
- Python 3.12 What's New confirms PEP 695 -- https://docs.python.org/3.12/whatsnew/3.12.html
- Python 3.10 What's New has no mention of PEP 695 -- https://docs.python.org/3.10/whatsnew/3.10.html

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
