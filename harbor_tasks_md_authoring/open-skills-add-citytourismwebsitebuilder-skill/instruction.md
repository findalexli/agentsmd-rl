# Add city-tourism-website-builder skill

Source: [besoeasy/open-skills#6](https://github.com/besoeasy/open-skills/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/city-tourism-website-builder/SKILL.md`

## What to add / change

This PR adds a new skill for creating modern, animated tourism websites for cities.

**Features:**
- Deep research workflow for gathering historical facts and tourist attractions
- Modern colorful design with white background
- Smooth animations (floating shapes, fade-ins, hover effects)
- Responsive layout for all devices
- IPFS deployment guide

**Includes:**
- Complete SKILL.md documentation
- Research methodology
- Design principles and CSS patterns
- Technical implementation guide
- Best practices for content and performance

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
