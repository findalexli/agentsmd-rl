# fix: boundary-aware contour extraction to eliminate woodcut artifacts

Source: [oaustegard/claude-skills#467](https://github.com/oaustegard/claude-skills/pull/467)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `image-to-svg/SKILL.md`

## What to add / change

## Summary

Replaces Step 4 (Contour Extraction) with a boundary-aware version that eliminates harsh "woodcut" outline artifacts.

## Changes (v1.2)

- **Step 3b (new)**: Generates structural edge map via `seeing-images` skill
- **Step 4**: Two fixes:
  1. Non-dark cluster masks dilated by 3×3 kernel — fills dark boundary gaps
  2. Dark shapes gated by compactness + edge-map alignment — keeps real features, skips thin boundary artifacts
- **Anti-pattern #8 (new)**: Don't use dilation kernel >3×3
- **Dependencies**: Cross-skill dependency on `seeing-images`
- **Version**: 1.0.0 → 1.2.0

## Threshold Calibration (v1.1 → v1.2)

v1.1 thresholds (compact > 0.15, edge > 0.3) were too aggressive — on the Mona Lisa, they filtered 36 dark shapes but only 4 were genuine artifacts. The other 32 were facial detail (nostrils, lip shadows, brow lines) that share the same thin/dark signature as boundary artifacts.

v1.2 thresholds (compact > 0.08, edge > 0.15) filter only the truly artifactual shapes:

| Image | v1.1 filtered | v1.2 filtered |
|-------|-------------|-------------|
| Mona Lisa | 36 | 4 |
| Portrait | ~36 | 8 |
| Kandinsky | 0 | 0 |

## Visual Results

v1.2 eliminates woodcut lines while preserving facial definition. The dilation fix (mechanism 1) does ~90% of the work; the gating (mechanism 2) is conservative cleanup.

Fixes #466

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
