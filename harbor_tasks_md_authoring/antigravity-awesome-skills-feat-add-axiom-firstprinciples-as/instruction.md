# feat: add axiom first-principles assumption auditor

Source: [sickn33/antigravity-awesome-skills#508](https://github.com/sickn33/antigravity-awesome-skills/pull/508)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/axiom/SKILL.md`
- `skills/axiom/examples/walkthrough-en.md`
- `skills/axiom/examples/walkthrough-zh.md`
- `skills/axiom/references/assumption-types.md`
- `skills/axiom/references/scenarios.md`

## What to add / change

# Pull Request Description

Adds `axiom` — a bilingual (Chinese/English) first-principles assumption auditor skill.

Instead of generic "list your assumptions" prompts, Axiom introduces a structured 5-phase process:
1. **Reframe** the question itself before touching assumptions
2. **Mine** 8-12 hidden assumptions across 3 depth layers
3. **Classify** each as 🔵 Physical Fact / 🟡 Convention / 🔴 Belief / ⚫ Interest-Driven
4. **Rank** by Fragility × Impact → output "Top 3 Most Dangerous Assumptions"
5. **Rebuild** conclusions from verified premises, showing cognitive shift

Key differentiators:
- Bilingual: auto-detects Chinese or English input and responds in the same language
- 4-type classification system with different challenge strategies per type
- Anti-sycophancy hard constraints (no flattery, no agreeing with user's original conclusion)
- 8 scenario-specific mining checklists with culturally-localized hidden assumptions

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

**All applicable items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`safe`).
- [x] **Triggers**: The "When to use" section is clear and s

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
