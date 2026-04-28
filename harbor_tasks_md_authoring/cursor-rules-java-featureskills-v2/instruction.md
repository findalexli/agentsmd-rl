# Feature/skills v2

Source: [jabrena/cursor-rules-java#418](https://github.com/jabrena/cursor-rules-java/pull/418)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/110-java-maven-best-practices/SKILL.md`
- `.agents/skills/111-java-maven-dependencies/SKILL.md`
- `.agents/skills/hello-world/SKILL.md`

## What to add / change

# Rationale for this change

Explain the reasons to change the repository

# What changes are included in this PR?

Explain what changes do this PR

# Are these changes tested?

Explain if the PR was tested and explain details

# Are there any user-facing changes?

Explain if the PR will impact the final user

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
