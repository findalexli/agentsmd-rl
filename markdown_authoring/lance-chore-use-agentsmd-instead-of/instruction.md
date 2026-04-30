# chore: use AGENTS.md instead of CLAUDE.md

Source: [lance-format/lance#4851](https://github.com/lance-format/lance/pull/4851)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`
- `java/AGENTS.md`
- `java/CLAUDE.md`
- `java/CLAUDE.md`
- `protos/AGENTS.md`
- `protos/CLAUDE.md`
- `protos/CLAUDE.md`
- `python/AGENTS.md`
- `python/CLAUDE.md`
- `python/CLAUDE.md`

## What to add / change

This PR will rename `CLAUDE.md` to `AGENTS.md` instead to allow other code agents can work well on lance. We keep the `CLAUDE.md` as an alias.

---

**This PR was primarily authored with Codex using GPT-5-Codex and then hand-reviewed by me. I AM responsible for every change made in this PR. I aimed to keep it aligned with our goals, though I may have missed minor issues. Please flag anything that feels off, I'll fix it quickly.**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
