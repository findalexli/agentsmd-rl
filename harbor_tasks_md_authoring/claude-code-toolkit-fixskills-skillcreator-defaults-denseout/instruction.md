# fix(skills): skill-creator defaults + dense-output directive

Source: [notque/claude-code-toolkit#526](https://github.com/notque/claude-code-toolkit/pull/526)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skill-creator/SKILL.md`

## What to add / change

## Summary

ADR-173 surfaced drift in skill-creator: it was silent on the default value of `user_invocable`, did not require INDEX.json regeneration after scaffolding, had no joy-check integration, and imposed no output-style constraint on generated skills.

- **Output style directive** near the top: generated SKILL.md and agent bodies must be dense informational text focused on accuracy. No filler, no pep talk, prefer tables and bullet lists over paragraphs.
- **`user_invocable: false` is the default.** Flipping to `true` requires an explicit justification comment in the frontmatter naming the user-facing trigger phrases and why `/do` routing is insufficient.
- **Post-scaffold INDEX regeneration** is now a mandatory step: `python3 scripts/generate-skill-index.py`. Without it the router cannot discover the new skill.
- **Joy-check + do-pair validation** documented as post-scaffold checks, with `scripts/validate-references.py --check-do-framing` as the accepted deterministic substitute for structural pairing.

Minimal text edits; no structural refactor of the skill.

**agent-creator status:** does not exist in the repo. Not scaffolded (user did not ask for creation). Reported as follow-up.

## Test plan

- [x] YAML frontmatter parses
- [x] `ruff check` + `ruff format --check` pass
- [x] `scripts/validate-references.py --check-do-framing` exits 0
- [ ] CI green on PR

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
