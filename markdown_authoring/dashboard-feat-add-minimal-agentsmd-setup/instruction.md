# feat: add minimal AGENTS.md setup

Source: [gardener/dashboard#2622](https://github.com/gardener/dashboard/pull/2622)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `backend/AGENTS.md`
- `frontend/AGENTS.md`

## What to add / change

**What this PR does / why we need it**:
Add minimal AGENTS.md setup
**Which issue(s) this PR fixes**:
Fixes #

**Special notes for your reviewer**:

**Release note**:
<!--  Write your release note:
1. Enter your release note in the below block.
2. If no release note is required, just write "NONE" within the block.

Format of block header: <category> <target_group>
Possible values:
- category:       breaking|feature|bugfix|doc|other
- target_group:   user|operator|developer|dependency
-->
```other developer
Add minimal AGENTS.md setup
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
