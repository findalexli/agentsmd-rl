# Improve senior-fullstack skill description and add workflow validation

Source: [alirezarezvani/claude-skills#216](https://github.com/alirezarezvani/claude-skills/pull/216)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `engineering-team/senior-fullstack/SKILL.md`

## What to add / change

Hey @alirezarezvani, thanks you for putting this skills collection together! Kudos on soon hitting 2k stars. I just starred it.

was running your skills through some evals and noticed a few things on `senior-fullstack` that were pretty quick to improve (moving from `~43% to ~93%` agent performance):

- _frontmatter description_ wasn't matching prompts like "create a new app" or "audit my codebase". expanded it with specific actions and natural trigger clauses.
- Trigger Phrases section redundancy on what the frontmatter description already covers - trimmed it
- added scaffolding workflow to verify it succeeded before proceeding + audit workflow to re-run the analyzer after fixing issues

these were easy changes to bring the skill in line with what performs well against **Anthropic's best practices**. honest disclosure, I work at a company where we build tooling around this. not a pitch, just fixes that were straightforward to make.

you've got `50+` skills here, if you want to do it yourself, evals are free and open to run: [link](https://tessl.io/skills/github/alirezarezvani/claude-skills/senior-fullstack/review). otherwise happy to make the improvements for you

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
