# feat(skills): add baoyu-comic skill

Source: [NousResearch/hermes-agent#13257](https://github.com/NousResearch/hermes-agent/pull/13257)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/creative/baoyu-comic/PORT_NOTES.md`
- `skills/creative/baoyu-comic/SKILL.md`
- `skills/creative/baoyu-comic/references/analysis-framework.md`
- `skills/creative/baoyu-comic/references/art-styles/chalk.md`
- `skills/creative/baoyu-comic/references/art-styles/ink-brush.md`
- `skills/creative/baoyu-comic/references/art-styles/ligne-claire.md`
- `skills/creative/baoyu-comic/references/art-styles/manga.md`
- `skills/creative/baoyu-comic/references/art-styles/minimalist.md`
- `skills/creative/baoyu-comic/references/art-styles/realistic.md`
- `skills/creative/baoyu-comic/references/auto-selection.md`
- `skills/creative/baoyu-comic/references/base-prompt.md`
- `skills/creative/baoyu-comic/references/character-template.md`
- `skills/creative/baoyu-comic/references/layouts/cinematic.md`
- `skills/creative/baoyu-comic/references/layouts/dense.md`
- `skills/creative/baoyu-comic/references/layouts/four-panel.md`
- `skills/creative/baoyu-comic/references/layouts/mixed.md`
- `skills/creative/baoyu-comic/references/layouts/splash.md`
- `skills/creative/baoyu-comic/references/layouts/standard.md`
- `skills/creative/baoyu-comic/references/layouts/webtoon.md`
- `skills/creative/baoyu-comic/references/ohmsha-guide.md`
- `skills/creative/baoyu-comic/references/partial-workflows.md`
- `skills/creative/baoyu-comic/references/presets/concept-story.md`
- `skills/creative/baoyu-comic/references/presets/four-panel.md`
- `skills/creative/baoyu-comic/references/presets/ohmsha.md`
- `skills/creative/baoyu-comic/references/presets/shoujo.md`
- `skills/creative/baoyu-comic/references/presets/wuxia.md`
- `skills/creative/baoyu-comic/references/storyboard-template.md`
- `skills/creative/baoyu-comic/references/tones/action.md`
- `skills/creative/baoyu-comic/references/tones/dramatic.md`
- `skills/creative/baoyu-comic/references/tones/energetic.md`
- `skills/creative/baoyu-comic/references/tones/neutral.md`
- `skills/creative/baoyu-comic/references/tones/romantic.md`
- `skills/creative/baoyu-comic/references/tones/vintage.md`
- `skills/creative/baoyu-comic/references/tones/warm.md`
- `skills/creative/baoyu-comic/references/workflow.md`

## What to add / change

## Summary

- Adds a new `baoyu-comic` skill under `skills/creative/`, a knowledge/educational comic creator with 6 art styles × 7 tones × 7 layouts + 5 presets (ohmsha, wuxia, shoujo, concept-story, four-panel).
- Ported from upstream [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.56.1, adapted to match the style of the existing [baoyu-infographic](skills/creative/baoyu-infographic/) port.
- Uses Hermes built-ins: `clarify` for user questions (one at a time, not batched), `image_generate` for rendering, `write_file`/`read_file` for I/O. PDF assembly is dropped (no `pdf-lib` dependency) — pages are delivered as individual PNGs.

## Hermes adaptations

| Change | Why |
|--------|-----|
| `openclaw` → `hermes` metadata | Hermes skill format |
| Slash-command / CLI-flag triggers dropped | Hermes uses natural-language skill matching |
| `EXTEND.md` preferences system removed (`references/config/` + workflow Step 1.1) | Not part of Hermes infra |
| `AskUserQuestion` (batched) → `clarify` (one at a time) | Hermes equivalent |
| `baoyu-imagine` (supports `--ref`) → `image_generate` (prompt-only, returns a URL) | Hermes built-in; no reference-image input, so character consistency is driven by text descriptions embedded in every page prompt, and every returned URL is downloaded (`curl -fsSL`) to the output directory |
| PDF merge (`scripts/merge-to-pdf.ts` + `pdf-lib`) removed | Would require a new dependency not declared anywhere in Hermes; out of scope for this por

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
