# improve changelog-generator skill structure + eval score

Source: [ECNU-ICALK/AutoSkill#3](https://github.com/ECNU-ICALK/AutoSkill/pull/3)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md`

## What to add / change

hey @ECNU-ICALK, thanks for publishing AutoSkill. really like the experience-driven lifelong learning approach to skill self-evolution. Kudos on passing `250` stars! I've just starred it.

ran your changelog-generator skill through agent evals and spotted a few quick wins that took it from `~49%` to `~100%` performance:

- expanded description with trigger terms like _release notes, version history, semantic versioning, commit parsing_ so agents reliably match user requests

- restructured into clear workflow steps + added verification checkpoints for changelog quality

- cut verbose educational content + tightened into actionable tables and rules

these were easy changes to bring the skill in line with what **performs well against Anthropic's best practices**. honest disclosure, I work at tessl.io where we build tooling around this. not a pitch, just fixes that were straightforward to make!

you've got `5896` skills, if you want to do it yourself, spin up Claude Code and run `tessl skill review`. alternatively, let me know if you'd like an automatic review in your repo via GitHub Actions. it doesn't require signup, and this means you and your contributors get an instant quality signal before you have to review yourself.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
