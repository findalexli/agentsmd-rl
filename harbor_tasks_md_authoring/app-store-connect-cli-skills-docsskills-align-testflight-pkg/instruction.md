# docs(skills): align TestFlight + PKG upload commands

Source: [rorkai/app-store-connect-cli-skills#10](https://github.com/rorkai/app-store-connect-cli-skills/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/asc-release-flow/SKILL.md`
- `skills/asc-testflight-orchestration/SKILL.md`
- `skills/asc-xcode-build/SKILL.md`

## What to add / change

## Summary
- Fix TestFlight commands in `asc-testflight-orchestration` to use `asc testflight beta-groups` and `asc testflight beta-testers`.
- Update macOS upload guidance in `asc-xcode-build` and `asc-release-flow` to use `asc builds upload --pkg` (remove outdated `altool` flow).

## Test plan
- [ ] Read the updated skill docs for correctness.
- [ ] Spot-check against `asc --help` and `asc builds upload --help`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
