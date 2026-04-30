# Fix stale test project references in CLAUDE.md

Source: [gui-cs/Terminal.Gui#5070](https://github.com/gui-cs/Terminal.Gui/pull/5070)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

The Build & Test section of `CLAUDE.md` referenced a `Tests/UnitTests` project that no longer exists. The actual test projects are `UnitTestsParallelizable`, `UnitTests.NonParallelizable`, and `UnitTests.Legacy` (per `Tests/README.md`). Copy-pasting the documented `dotnet test` command would fail.

- Replaced the stale `Tests/UnitTests` reference with the three current projects, each annotated with when to use it.
- Added a single-test `--filter` example.
- Added a pointer to `Tests/README.md` for the full list of test projects and the static-state classification that determines where a new test belongs.
- Updated the "Testing" summary bullet to reflect the three-project split and the rule that new tests never go in `UnitTests.Legacy`.

Docs-only change — no code, tests, or warnings affected.

## Test plan

- [x] `CLAUDE.md` renders correctly on GitHub
- [x] The `dotnet test --project Tests/UnitTestsParallelizable --no-build` command in the doc matches a real project path
- [x] No source files touched, so no new warnings possible

# To pull down this PR locally:
```
git remote add copilot https://github.com/harder/Terminal.Gui.git
git fetch copilot docs/claude-md-fix-test-projects
git checkout copilot/docs/claude-md-fix-test-projects
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
