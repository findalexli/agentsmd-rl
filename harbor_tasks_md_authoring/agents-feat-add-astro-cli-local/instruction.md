# feat: add Astro CLI local development skills

Source: [astronomer/agents#18](https://github.com/astronomer/agents/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `shared-skills/astro-local-env/SKILL.md`
- `shared-skills/astro-project-setup/SKILL.md`

## What to add / change

## Summary
- Add `astro-project-setup` skill for initializing projects, managing dependencies, and configuring connections/variables
- Add `astro-local-env` skill for starting/stopping/restarting the local environment, viewing logs, and troubleshooting container issues
- These complement existing MCP-based skills by covering the container lifecycle *before* Airflow is running

Closes #17 

## Test plan
- [ ] Install plugin and verify skills are discovered
- [ ] Test `/data:astro-project-setup` triggers on "init project", "new Airflow project"
- [ ] Test `/data:astro-local-env` triggers on "start Airflow", "restart", "view logs"

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
