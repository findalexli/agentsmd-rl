# Add Gingiris Growth Playbooks to Skills Collection

Source: [davepoon/buildwithclaude#94](https://github.com/davepoon/buildwithclaude/pull/94)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/gingiris-growth-playbooks/SKILL.md`

## What to add / change

Hi Dave,

As requested in Issue #89, here is the PR adding the Gingiris Growth Playbooks as a skill in the collection.

## What's included

A single `SKILL.md` file at `plugins/all-skills/skills/gingiris-growth-playbooks/SKILL.md` that documents 4 open-source growth playbooks:

- **gingiris-launch**: AI Product Launch Playbook (Product Hunt #1 strategy, KOL, UGC, Reddit)
- **gingiris-b2b-growth**: B2B Growth Playbook (PLG, SLG, affiliate, partner channels)
- **gingiris-opensource**: Open Source Launch Playbook (GitHub star growth, HN Show HN, community)
- **gingiris-aso-growth**: ASO & App Growth Playbook (iOS/Android keyword research, UGC)

All playbooks are MIT licensed, markdown-based, and require no MCP or API keys.

Closes #89

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
