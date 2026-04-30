# Improve performance-benchmark/SKILL.md

Source: [dotnet/runtime#124574](https://github.com/dotnet/runtime/pull/124574)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/performance-benchmark/SKILL.md`

## What to add / change

1. Copilot sometimes wraps the command into a code block too - told it to avoid that
2. Removed the -commit mode, Copilot typically works inside PRs only anyway, so let's make the skill smaller
3. Recommended it to prefer `osx_arm64` target. EgorBot uses Helix for it and it's baremetal so it's free (for me) and is the fastest. Also, the fact that it's baremetal makes the results more stable.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
