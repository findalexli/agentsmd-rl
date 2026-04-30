# SKILL.md: reframe post-task ritual as "Always contribute back"

Source: [browser-use/browser-harness#61](https://github.com/browser-use/browser-harness/pull/61)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

- Renames the **Post-task ritual** section to **Always contribute back** and rewrites it as the default procedure — not an optional nicety.
- Adds concrete examples of what's worth a PR (private APIs, framework quirks, stable selectors, URL patterns, waits, traps) so agents know what to look for.
- Adds a short **What a domain skill should capture** schema — the durable shape of the site, not the diary of the run.
- Adds an explicit **Do not write** list — most importantly banning **raw pixel coordinates**, which rot on any viewport/zoom/layout change.
- Narrows scope to `domain-skills/` only. Removed the previous nudges to update `interaction-skills/` or `helpers.py` from this loop — that's a separate decision, not a contribution default.

Inspired by Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) idea of making the agent a disciplined maintainer, adapted to our single-layer `domain-skills/` setup (no index/log/lint — those are already covered by `ls` and `git log`).

## Test plan

- [ ] Read the new section end-to-end on GitHub and confirm the imperative tone reads right.
- [ ] Sanity-check that the examples (React combobox, Vue scroll container, `?th=1`) are grounded in real patterns already seen in `domain-skills/`.
- [ ] Verify the "no raw coordinates" rule would actually flag the weaker parts of `domain-skills/tiktok/upload.md` as things to improve next time.

🤖 Generated with [Claude Code](https://claude.com/claude-

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
