# feat: add pricing.md guidance to ai-seo skill

Source: [coreyhaines31/marketingskills#208](https://github.com/coreyhaines31/marketingskills/pull/208)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-seo/SKILL.md`

## What to add / change

## Summary
- Adds new "Machine-Readable Files for AI Agents" subsection to the ai-seo skill covering the agents-as-buyers trend
- Recommends adding a `/pricing.md` file with structured pricing data so AI agents can evaluate products programmatically
- Includes template format, best practices, and `llms.txt` mention
- Updates SaaS Product Pages section to reference pricing.md
- Adds "hiding pricing" as a common mistake anti-pattern
- Bumps version to 1.2.0

Inspired by [Zeno Rocha's tweet](https://x.com/zenorocha/status/2038361562856165629) on making pricing agent-readable.

## Test plan
- [ ] Verify SKILL.md is under 500 lines (currently 443)
- [ ] Verify YAML frontmatter is valid
- [ ] Review pricing.md template for completeness

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
