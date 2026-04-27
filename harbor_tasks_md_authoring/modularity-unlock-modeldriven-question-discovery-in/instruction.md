# Unlock model-driven question discovery in review and design skills

Source: [vladikk/modularity#2](https://github.com/vladikk/modularity/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/high-level-design/SKILL.md`
- `skills/review/SKILL.md`

## What to add / change

# Question Flexibility

This PR changes how the review and high-level-design skills gather information from users. The short version: **the model now reads the code first and figures out what to ask, instead of following a fixed questionnaire.**

## Why this matters

Your Balanced Coupling model is powerful — it needs three dimensions (strength, distance, volatility) to assess coupling properly. The model already has this framework loaded. But the current skills don't trust it to use that knowledge. Instead, they follow a rigid script:

1. Ask "Domain?" (fixed free-text prompt)
2. Ask "Teams?" (3 hard-coded options: Same team / Multiple teams / Mixed)
3. Ask "Pain points?" (3 hard-coded options: Yes / No / Not sure)

These questions fire every time regardless of what the code or requirements already reveal. The model is perfectly capable of reading the code, applying the Balanced Coupling lens, and discovering what information it actually needs — we just weren't letting it.

## What changed

### Review skill — Step 1 rewritten

**Before:** Read requirements → Ask Scope → Read code → Ask Domain (fixed) → Ask Teams (fixed) → Ask Pain points (fixed)

**After:** Ask Scope → Read code + requirements → **Surface understanding** (model presents what it learned, user validates/corrects) → **Discover gaps** (model identifies what's missing for coupling assessment, asks targeted questions)

The model now:
- Reads code **before** asking domain questions (was backw

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
