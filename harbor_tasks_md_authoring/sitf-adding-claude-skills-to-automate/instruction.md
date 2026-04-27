# Adding Claude Skills to automate attack flow creation and PRs for new techniques

Source: [wiz-sec-public/SITF#2](https://github.com/wiz-sec-public/SITF/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/attack-flow/SKILL.md`
- `.claude/skills/technique-proposal/SKILL.md`

## What to add / change

## Summary
  - Add `/attack-flow` skill: Generate SITF-compliant attack flow JSON from attack descriptions or incident reports
  - Add `/technique-proposal` skill: Generate PR-ready technique proposals when attacks don't map to existing SITF techniques

  ## Test plan
  - [x] Run `/attack-flow solarwinds websearch` and verify valid JSON output
  - [x] Run `/technique-proposal` for identified gaps and verify technique schema

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
