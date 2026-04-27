# feat: add community-marketing skill

Source: [coreyhaines31/marketingskills#78](https://github.com/coreyhaines31/marketingskills/pull/78)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/community-marketing/SKILL.md`

## What to add / change

## New Skill: community-marketing

### Description
Adds a new `community-marketing` skill that guides AI agents in building and leveraging online communities to drive product growth and brand loyalty.

### Skill Checklist
- [x] `name` matches directory name (`community-marketing`)
- [x] `description` clearly explains when to use the skill, with trigger phrases
- [x] Instructions are clear and actionable
- [x] No sensitive data or credentials
- [x] Follows existing skill patterns in the repo

### What this skill covers
- Community strategy principles (identity, value, flywheel model)
- Playbooks for launching from zero, growing existing communities, building ambassador programs, and community-led support
- Platform selection guide (Discord, Slack, Circle, Reddit, Facebook Groups, Discourse)
- Community health metrics and warning signs
- Output format options (strategy doc, channel architecture, new member journey, ritual calendar, ambassador program brief, health audit)

### Why this skill is needed
Community-led growth is a major acquisition and retention channel, especially for developer tools, SaaS products, and creator platforms. No existing skill in the repo covers this area - it sits adjacent to `referral-program`, `churn-prevention`, and `social-content` but is distinct from all of them.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
