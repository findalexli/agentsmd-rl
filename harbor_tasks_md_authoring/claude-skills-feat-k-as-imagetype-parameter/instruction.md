# feat: K as image-type parameter + isolation filter + higher K default

Source: [oaustegard/claude-skills#469](https://github.com/oaustegard/claude-skills/pull/469)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `image-to-svg/SKILL.md`

## What to add / change

## Summary

Three improvements building on the v1.3 boundary fixes (merged in #468).

## Changes

### K as a decision parameter (Step 2)
K is no longer a hardcoded range — Claude chooses based on the image:

| Image type | K | Rationale |
|-----------|---|-----------|
| Photo — portrait, landscape, still life | 56–64 | Faces need many skin tone steps |
| Painting — Renaissance, Impressionist | 48–64 | Sfumato, blending need tonal range |
| Illustration — comics, editorial | 36–48 | Moderate palette |
| Graphic art — logos, Kandinsky, flat design | 24–32 | Flat fills ARE correct |
| Pixel art, posterized | 8–16 | Match source palette |

Default 48 when uncertain. Decision criterion: "gradients or hard edges?"

### Isolation filter (Step 4, FIX 3)
Small dark shapes (<500px) surrounded by non-dark territory (dark_ratio < 0.3) are boundary artifacts. At higher K, more of these appear as scattered slivers in light regions.

Tested on Mona Lisa K=64: removes 37 slivers, keeps 670 real features.

### Batched label assignment
Full NxK distance matrix blows memory at K=64. Batched at 50K pixels per chunk.

### Updated file size guidelines
K=48-64 produces 1500-2500 paths, 800KB-1.2MB SVG.

## Test Results (Mona Lisa)
- K=32: 1048 shapes, 550KB — posterized
- K=48: 1808 shapes, 894KB — good
- K=64: 2312 shapes, 1.2MB — substantially better tonal gradation

Relates to #466

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
