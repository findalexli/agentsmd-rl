# feat: add image support to whiteboard-cli skill

Source: [larksuite/cli#553](https://github.com/larksuite/cli/pull/553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-whiteboard/references/content.md`
- `skills/lark-whiteboard/references/image.md`
- `skills/lark-whiteboard/references/layout.md`
- `skills/lark-whiteboard/references/schema.md`
- `skills/lark-whiteboard/routes/dsl.md`
- `skills/lark-whiteboard/scenes/photo-showcase.md`

## What to add / change

- Add references/image.md with image processing workflow
- Update content.md with strict image trigger condition
- Update schema.md with Image node type definition
- Update layout.md with image card layout rules
- Add scenes/photo-showcase.md for image showcase layouts
- Add photo-showcase to DSL route scene index
- Strict trigger: only when user explicitly requests images/配图/插图

## Summary

Add image/photo support to the lark-whiteboard skill. When users explicitly request images (图片/配图/插图), the DSL route uses the new `photo-showcase` scene to generate card-grid or timeline layouts with real uploaded photos via Drive file tokens.

## Changes

- Add `references/image.md`: image preparation workflow (download → md5 dedup → upload to Drive → collect file_tokens)
- Update `references/content.md`: strict image trigger condition — only when user explicitly says 图片/配图/插图
- Update `references/schema.md`: Image node type definition with upload steps and usage examples
- Update `references/layout.md`: image card layout rules (3:2 ratio, gap 24, vertical frame)
- Add `scenes/photo-showcase.md`: card-grid and route-timeline layout skeletons with valid WBDocument format
- Update `routes/dsl.md`: add photo-showcase to scene index table

## Test Plan

- [x] Manual local verification: rendered test images (GitHub avatar + cooking mindmap with 4 Unsplash images) using `whiteboard-cli`, confirmed image nodes display correctly
- [x] DSL JSON skeletons validated against 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
