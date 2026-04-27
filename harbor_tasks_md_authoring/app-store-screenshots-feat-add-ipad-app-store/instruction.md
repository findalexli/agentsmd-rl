# feat: Add iPad App Store screenshot support

Source: [ParthJadhav/app-store-screenshots#2](https://github.com/ParthJadhav/app-store-screenshots/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/app-store-screenshots/SKILL.md`

## What to add / change

## What

Adds iPad support to the App Store screenshot generator skill — CSS-only iPad Pro frame, export sizes, device toggle, and layout guidance.

## Changes to SKILL.md

- **iPad mockup component**: CSS-only iPad Pro frame (no external PNG asset needed). Uses `770/1000` aspect ratio so the inner screen area (92% × 94.4%) matches the 3:4 iPad screenshot ratio.
- **iPad export sizes**: 13" iPad (2064×2752) and 12.9" iPad Pro (2048×2732)
- **Device toggle**: iPhone/iPad toggle in toolbar, with `?device=ipad` URL param for headless/automated capture
- **File structure**: Added `screenshots-ipad/` directory convention
- **Architecture**: Updated to show dual-device component structure
- **Layout guidance**: iPad-specific sizing (65-70% width vs 82-86% for iPhone), font scaling from `canvasW`
- **Updated questions**: Added optional iPad screenshot prompt

## Why

The original skill only generates iPhone screenshots. Most iOS apps are universal and benefit from iPad screenshots too — they're required for iPad-only apps and improve App Store listing quality. The CSS-only approach means no additional mockup assets are needed.

## Tested with

Built and shipped iPad + iPhone App Store screenshots for a production app using this updated skill. The CSS iPad frame renders correctly at all export resolutions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
