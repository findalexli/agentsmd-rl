# Add reasoning-semiformally skill

Source: [oaustegard/claude-skills#522](https://github.com/oaustegard/claude-skills/pull/522)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `reasoning-semiformally/SKILL.md`

## What to add / change

Extracts the semi-formal reasoning templates from the blog post into a standalone skill.

**What:** Three certificate templates (patch verification, fault localization, patch equivalence) as cognitive forcing functions for code analysis.

**Why:** The templates proved effective in our replication of Ugare & Chandra (2026) — +11pp fault localization on real bugs. Currently the methodology lives only in the blog post and the verify_patch utility. This skill makes it discoverable and applicable to direct reasoning (not just sub-agent calls).

**Design:**
- Single SKILL.md (137 lines) — templates are compact enough to be the core content
- Points to `verify_patch` utility for the automated PR workflow path
- Includes when-to-apply / when-to-skip guidance (value scales with reasoning distance)
- Composing section for chaining templates on complex tasks

**Provenance:** [Blog post](https://austegard.com/blog/replicating-agentic-code-reasoning/), [semiformal_templates.md](https://github.com/oaustegard/muninn.austegard.com/blob/main/blog/replicating-agentic-code-reasoning/semiformal_templates.md)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
