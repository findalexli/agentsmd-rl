# fix: add missing sections to community-marketing skill

Source: [coreyhaines31/marketingskills#222](https://github.com/coreyhaines31/marketingskills/pull/222)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/community-marketing/SKILL.md`

## What to add / change

## Summary
- Adds Task-Specific Questions section (6 questions)
- Adds Related Skills section (referrals, churn-prevention, social, customer-research)

Content-only portion of the community-marketing cleanup (rename deferred to v2.0.0).

## Test plan
- [ ] Verify SKILL.md frontmatter is valid
- [ ] Confirm new sections follow skill spec conventions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
