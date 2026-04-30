# feat(skills): add himalaya-mail skill

Source: [wecode-ai/Wegent#556](https://github.com/wecode-ai/Wegent/pull/556)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `backend/init_data/skills/browser/SKILL.md`
- `backend/init_data/skills/himalaya-mail/SKILL.md`

## What to add / change

Changes:
- Add new skill init data: backend/init_data/skills/himalaya-mail/SKILL.md
- Minor wording tweak in backend/init_data/skills/browser/SKILL.md

Notes:
- Himalaya Mail skill includes folder localization (e.g. "已发送邮件") and safe send/mutate confirmations.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Introduced comprehensive documentation for the new Himalaya CLI-based email management skill, featuring safety-first operation patterns, confirmation workflows for destructive actions, and credential protection best practices
  * Updated browser skill documentation with minor corrections

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
