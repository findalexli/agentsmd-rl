# feat: add growth experimentation program to ab-test-setup

Source: [coreyhaines31/marketingskills#211](https://github.com/coreyhaines31/marketingskills/pull/211)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ab-test-setup/SKILL.md`

## What to add / change

## Summary
- Adds "Growth Experimentation Program" section covering the continuous experiment loop
- Includes ICE prioritization framework, hypothesis generation sources, experiment velocity metrics
- Adds experiment playbook pattern for documenting and scaling winning tests
- Adds experiment cadence (weekly/bi-weekly/monthly/quarterly review rhythm)
- Updates description with growth experimentation trigger phrases
- Bumps version to 1.2.0

Inspired by Eric Siu's autonomous experiment engine — adapted from executable scripts to strategic guidance that works across any testing tool.

## Test plan
- [ ] Verify SKILL.md under 500 lines (currently 349)
- [ ] Verify new section integrates naturally with existing test design content

Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
