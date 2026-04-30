# feat: add bdistill behavioral-xray and knowledge-extraction skills

Source: [sickn33/antigravity-awesome-skills#366](https://github.com/sickn33/antigravity-awesome-skills/pull/366)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bdistill-behavioral-xray/SKILL.md`
- `skills/bdistill-knowledge-extraction/SKILL.md`

## What to add / change

# Pull Request Description

## Summary

- **bdistill-behavioral-xray**: X-ray any AI model's behavioral patterns — refusal boundaries, hallucination tendencies, reasoning style, formatting defaults. The agent probes itself (no API key needed), generates a visual HTML report with radar charts and actionable insights.
- **bdistill-knowledge-extraction**: Extract domain-specific knowledge from open-source LLMs via Ollama. Medical, legal, cybersecurity, finance presets or custom terms. Produces structured reference data and exportable datasets.

Both skills are powered by the [bdistill](https://github.com/FrancyJGLisboa/bdistill) MCP server (`pip install bdistill`).

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

Use this only when the PR should auto-close an issue:

_No linked issue._

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Safety scan**: If this PR adds or modifies `

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
