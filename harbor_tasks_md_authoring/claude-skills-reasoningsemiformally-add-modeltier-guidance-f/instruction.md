# reasoning-semiformally: add model-tier guidance from CVE experiment

Source: [oaustegard/claude-skills#523](https://github.com/oaustegard/claude-skills/pull/523)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `reasoning-semiformally/SKILL.md`

## What to add / change

Adds model-tier guidance and CVE-2026-29000 experiment results to the reasoning-semiformally skill (merged in #522).

**New finding:** Semi-formal template value is model-capability-dependent.

| Model | Standard | Semi-formal | Delta |
|-------|----------|-------------|-------|
| Haiku 4.5 | 80% | 100% | +20pp |
| Sonnet 4.6 | 100% | 80% | -20pp |

Tested on CVE-2026-29000 (pac4j-jwt auth bypass, CVSS 10.0, 383 lines, vague symptom). Templates help smaller models bridge reasoning gaps but add token overhead that can hurt larger models on bugs within their native capacity.

**Practical implication:** Haiku + semi-formal ≈ Sonnet standard at ~1/10th cost.

**Changes:**
- Added "Model-Tier Considerations" section with decision framework
- Updated Provenance with CVE experiment results
- 154 lines total (was 137)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
