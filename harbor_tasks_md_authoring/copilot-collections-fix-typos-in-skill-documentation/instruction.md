# Fix typos in skill documentation files

Source: [TheSoftwareHouse/copilot-collections#10](https://github.com/TheSoftwareHouse/copilot-collections/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/architecture-design/SKILL.md`
- `.github/skills/code-review/SKILL.md`
- `.github/skills/task-analysis/SKILL.md`

## What to add / change

Addresses spelling errors in skill documentation files identified in PR #6 review.

**Changes:**

**`.github/skills/architecture-design/SKILL.md`:**
- Fixed "ambigious" → "ambiguous" (lines 18, 30)
- Fixed "Create a implementation" → "Create an implementation" (line 20)
- Fixed "untill" → "until" (line 32)
- Fixed "scallable" → "scalable" (line 39)

**`.github/skills/code-review/SKILL.md`:**
- Fixed "formating" → "formatting" (lines 22, 62)
- Fixed "scallable" → "scalable" (lines 24, 70)

**`.github/skills/task-analysis/SKILL.md`:**
- Fixed "reasearch" → "research" (lines 19, 47)
- Fixed "proceeed" → "proceed" (line 45)
- Fixed "untill" → "until" (line 45)
- Fixed "informations" → "information" (line 49)

**`.github/skills/codebase-analysis/SKILL.md`:**
- Fixed "scallable" → "scalable" (line 83)

All corrections maintain consistency across the skill documentation files.

<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot coding agent [set things up for you](https://github.com/TheSoftwareHouse/copilot-collections/issues/new?title=✨+Set+up+Copilot+instructions&body=Configure%20instructions%20for%20this%20repository%20as%20documented%20in%20%5BBest%20practices%20for%20Copilot%20coding%20agent%20in%20your%20repository%5D%28https://gh.io/copilot-coding-agent-tips%29%2E%0A%0A%3COnboard%20this%20repo%3E&assignees=copilot) — coding agent works faster and does higher quality work when set up for your repo.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
