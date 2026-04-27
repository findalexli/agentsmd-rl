# fix: pre-load images as data URIs to prevent black exports

Source: [ParthJadhav/app-store-screenshots#13](https://github.com/ParthJadhav/app-store-screenshots/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/app-store-screenshots/SKILL.md`

## What to add / change

## Problem

`html-to-image`'s `toPng()` clones the DOM into an SVG `<foreignObject>` and re-fetches every `<img>` src during serialization. These re-fetches are **non-deterministic** — some hit the browser cache, some silently fail. Failed images render as transparent rectangles in the export.

When these RGBA exports are flattened to RGB for App Store upload (which rejects alpha), the transparent regions become solid black — producing phone mockups with black screens.

### What this looks like in practice

Building 6 App Store screenshots for an iOS app. All slides use the same source images. After export:

- Slides 1, 4, 6 → phone screens rendered correctly
- Slides 2, 3, 5 → phone screens are solid black

Same image (`url-scan.png`), same page, same export session — but different results per slide. The existing double-call trick only warms fonts, not image fetches in cloned DOM nodes.

### Additional issue: App Store rejects RGBA PNGs

Even when exports look correct, App Store Connect rejects uploads with `IMAGE_ALPHA_NOT_ALLOWED` if the source screenshots have alpha channels. The skill didn't mention this.

## Solution

Added to SKILL.md Step 6 (Export):

1. **Pre-load all images as base64 data URIs at page load** using a `preloadAllImages()` function and `imageCache` map
2. **Use an `img()` helper** in all slide components instead of raw file paths — when `html-to-image` clones the DOM, data URI sources are already inline, no fetch needed
3. **Gate rendering on preload c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
