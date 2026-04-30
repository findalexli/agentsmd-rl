# fix: boundary-aware contour extraction (v1.3.0)

Source: [oaustegard/claude-skills#468](https://github.com/oaustegard/claude-skills/pull/468)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `image-to-svg/SKILL.md`

## What to add / change

## Summary

Updates image-to-svg with boundary-aware contour extraction to fix woodcut artifacts.

## Changes

### Boundary fixes (Steps 3b, 4)
1. **Structural edge map** via `seeing-images` skill  
2. **Territory-aware dilation**: Non-dark masks dilate 3×3, but growth is masked against dark territory to prevent encroachment on hair/clothing boundaries
3. **Relaxed dark shape gating**: compact > 0.08, edge > 0.15 (filters only truly artifactual shapes)

### Other
- Anti-pattern #8: Don't use dilation > 3×3
- Cross-skill dependency on `seeing-images`
- Version: 1.0.0 → 1.3.0

## What was tried and reverted
- **Gradient fills** (per-shape linear gradient fitting): R² values were all <0.14 at K=32 granularity — shapes are too small for meaningful gradient detection. Result was color artifacts, not smooth transitions. Portrait became unrecognizable. Reverted.

## Test Results

| Image | Woodcut lines | Facial detail | Hair boundary |
|-------|-------------|--------------|--------------|
| Mona Lisa | Eliminated | Preserved | Natural |
| Portrait | Eliminated | Preserved | Natural |
| Kandinsky | N/A (hard-edge) | N/A | N/A |

Fixes #466

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
