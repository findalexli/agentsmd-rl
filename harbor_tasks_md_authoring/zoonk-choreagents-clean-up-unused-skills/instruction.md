# chore(agents): clean up unused skills

Source: [zoonk/zoonk#1317](https://github.com/zoonk/zoonk/pull/1317)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/zoonk-code-simplification/SKILL.md`
- `.agents/skills/zoonk-issue-writer/SKILL.md`
- `.agents/skills/zoonk-technical/SKILL.md`
- `.claude/agents/code-simplifier.md`
- `.claude/agents/prompt-reviewer.md`

## What to add / change

<!-- This is an auto-generated description by cubic. -->
## Summary by cubic
Removed unused agent skills and legacy Claude agent configs to reduce clutter and prevent outdated guidance in the repo. Deleted SKILLs `zoonk-code-simplification`, `zoonk-issue-writer`, `zoonk-technical` and `.claude/agents` configs `code-simplifier.md` and `prompt-reviewer.md`.

<sup>Written for commit 095f005766875eae20973946b7ac7b75b267568e. Summary will update on new commits. <a href="https://cubic.dev/pr/zoonk/zoonk/pull/1317?utm_source=github">Review in cubic</a></sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
