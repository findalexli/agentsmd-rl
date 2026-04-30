# Add some claude skills

Source: [ClickHouse/ClickHouse#95369](https://github.com/ClickHouse/ClickHouse/pull/95369)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `.claude/skills/build/SKILL.md`
- `.claude/skills/install-skills/SKILL.md`
- `.claude/skills/test/SKILL.md`

## What to add / change

### Changelog category (leave one):
- Not for changelog (changelog entry is not required)

If you have changes from this branch you need to ask claude code to `install skills`. This is initiall setup so it knows for other skills where the build folder is.
After that is modified you don't have to run it anymore.

The idea is to have some tasks which are done often stored as a skill (I guess something equivalent to module).
E.g. with build skill everytime you ask claude to build it will know what to do because of build skill.
Furthermore, subtasks in a skill are done by subagents so the context of your chat will not be polluted with useless output.
E.g. build output analysis is done by subagent and the main chat will only receive the summary, not the entire output.

Same things apply for test skill. You can run both stateless and integration tests by just telling claude to `run test test_name`.
Test output will be analyzed by subagent and only summary will be returned to the user.
You can tell explicitly which test to run or just say `run test` or `test`. In that case it will prompt you to pick a test, it will look at the current viewed file and if it's test it will offer that, otherwise you can just input the test name.

- [ ] Documentation is written (mandatory for new features)

<!---
Directly edit documentation source files in the "docs" folder with the same pull-request as code changes

or

Add a user-readable short description of the changes that sho

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
