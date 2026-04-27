# Add image-to-svg skill v1.0.0

Source: [oaustegard/claude-skills#457](https://github.com/oaustegard/claude-skills/pull/457)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `image-to-svg/SKILL.md`

## What to add / change

Data-driven image-to-SVG conversion skill.

**Pipeline:** preprocessing → K-means quantization → contour extraction → SVG assembly

**Core principle:** Trust the data, not your imagination. Every shape, color, and position comes from computational analysis of source pixels.

**Tested on:**
- Kandinsky's *Around the Circle* — 825 paths, 358KB, 20s (matches 31 iterations of hand-drawn SVG)
- Mona Lisa — 2,505 paths, 1.27MB, 75s (correlation 0.93)

**Dependencies:** opencv-python-headless, scikit-image, scipy, librsvg2-bin

Blog post: https://muninn.austegard.com/blog/trust-the-data-not-your-imagination.html

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
