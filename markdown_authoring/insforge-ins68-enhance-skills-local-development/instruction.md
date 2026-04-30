# INS-68: Enhance skills local development for new UI

Source: [InsForge/InsForge#1126](https://github.com/InsForge/InsForge/pull/1126)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/insforge-dev/dashboard/SKILL.md`
- `.claude/skills/insforge-dev/dashboard/SKILL.md`
- `.codex/skills/insforge-dev/dashboard/SKILL.md`

## What to add / change

## Summary

<!-- Briefly describe what this PR does -->

## How did you test this change?

<!-- Describe how you tested this PR -->
Test locally

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added internal developer documentation describing a local debug workflow to temporarily view cloud-only UI while running a self-hosted frontend.
  * Includes required comment convention for temporary edits and a detailed revert checklist to ensure all temporary changes are restored and checks (lint/typecheck, diff review) are performed before committing.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
