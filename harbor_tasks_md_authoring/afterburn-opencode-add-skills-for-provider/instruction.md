# opencode: add skills for provider scaffolding and release automation

Source: [coreos/afterburn#1268](https://github.com/coreos/afterburn/pull/1268)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/add-provider/SKILL.md`
- `.opencode/skills/prepare-release/SKILL.md`
- `.opencode/skills/publish-release/SKILL.md`

## What to add / change

Add three OpenCode skills to automate common repository workflows:

- add-provider: scaffold new cloud/platform providers with all required files, wiring, documentation, and tests
- prepare-release: create pre-release PR with dependency updates and drafted release notes
- publish-release: guide the post-merge release process including release branch, tag, vendor archive, and GitHub release

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
