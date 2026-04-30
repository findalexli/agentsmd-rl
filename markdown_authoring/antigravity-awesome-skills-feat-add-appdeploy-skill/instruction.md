# feat: add appdeploy skill

Source: [sickn33/antigravity-awesome-skills#134](https://github.com/sickn33/antigravity-awesome-skills/pull/134)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/appdeploy/SKILL.md`

## What to add / change

Adds the `appdeploy` skill to the Infrastructure category.

Chat-native deployment: deploy apps with frontend, backend, cron jobs, database, file storage, AI capabilities, auth, and notifications, and get back a live public URL instantly.

- Website: https://appdeploy.ai
- Skills repo: https://github.com/AppDeploy-AI/skills
- Validation passes in strict mode

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
