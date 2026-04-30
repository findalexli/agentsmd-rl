# docs(website-to-hyperframes): add load-bearing GSAP authoring rules

Source: [heygen-com/hyperframes#364](https://github.com/heygen-com/hyperframes/pull/364)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/website-to-hyperframes/references/step-6-build.md`

## What to add / change

## Summary

Adds a new **Load-bearing rules for animation authoring** subsection to `skills/website-to-hyperframes/references/step-6-build.md`, capturing five GSAP authoring rules the linter cannot catch but that silently ship broken output — compositions that pass lint and render elements invisible, unscrubbing, or frozen.

## Evidence

Surfaced from two independent website-to-hyperframes builds on 2026-04-20:
- `spatial-deck/promo/hyperframes-auto/` — single-page SPA source
- `~/harvardxr-auto/` — marketing-site source

Both lint-clean on the first try. Both rendered cleanly **only** because we injected these rules into the sub-agent prompt before dispatch. Without them, sub-agents produced lint-passing compositions with:
- Hero images that entered then vanished (stacked `y`-entrance + `scale` Ken Burns tweens on one element)
- Auras that looked right in the studio preview but were missing from the rendered MP4 (standalone `gsap.to()` that didn't scrub)
- Scene transitions where elements flashed visible before their own entrance (`gsap.from()` `immediateRender` interacting with `.clip` boundaries)

## Rules added

1. **No iframes for captured content** — don't seek deterministically, cannot scrub.
2. **Never stack two transform tweens on one element** — the second tween's `immediateRender` resets the first, element ends up invisible. With before/after code showing two fixes (combine into one `fromTo`, or split across parent/child wrappers).
3. **Prefer `tl.fromTo()` over `t

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
