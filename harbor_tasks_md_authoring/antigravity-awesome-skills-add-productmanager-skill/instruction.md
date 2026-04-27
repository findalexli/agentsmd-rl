# Add product-manager skill

Source: [sickn33/antigravity-awesome-skills#206](https://github.com/sickn33/antigravity-awesome-skills/pull/206)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/product-manager/SKILL.md`

## What to add / change

## Summary

- Adds a new `product-manager` skill to `skills/product-manager/SKILL.md`.
- Senior PM agent with 6 knowledge domains, 30+ frameworks, 12 templates, and 32 SaaS metrics with formulas.
- Pure Markdown, zero scripts. Source: [Digidai/product-manager-skills](https://github.com/Digidai/product-manager-skills).
- Follows the required SKILL.md frontmatter format (name, description, source, date_added).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
