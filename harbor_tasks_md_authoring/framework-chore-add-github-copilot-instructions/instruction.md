# chore: add GitHub Copilot instructions

Source: [goravel/framework#1438](https://github.com/goravel/framework/pull/1438)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary
- Add `.github/copilot-instructions.md` with Go code style, error handling, and testing rules for GitHub Copilot
- Enforce consistent import ordering, use of `any` over `interface{}`, and sentinel error declaration patterns
- Point to `.agents/prompts/tests.md` for the full testing guidelines

## Why
The repository had no structured file to guide GitHub Copilot when reviewing or generating code for `goravel/framework`. Without it, Copilot suggestions could diverge from the project's established conventions around error handling, code style, and testing.

Adding `.github/copilot-instructions.md` documents the key rules in one place — Go style (use `any`, import order, no variable shadowing), error handling (sentinel errors in `errors/list.go`, module tagging, no silent swallowing), and a pointer to the full testing guide — so that Copilot's review feedback and code suggestions stay consistent with project standards.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
