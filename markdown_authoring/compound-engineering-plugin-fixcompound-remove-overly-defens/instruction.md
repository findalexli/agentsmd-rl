# fix(compound): remove overly defensive context budget precheck

Source: [EveryInc/compound-engineering-plugin#279](https://github.com/EveryInc/compound-engineering-plugin/pull/279)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound/SKILL.md`

## What to add / change

## Summary

- Removes the Phase 0 "context budget check" that nagged users with a warning and forced them to choose between full/compact-safe mode — even with 80%+ context remaining
- Full mode now runs by default, no questions asked
- Compact-safe mode stays available if users explicitly request it

Fixes #278 — reported by [@NoamTenne on X](https://x.com/NoamTenne/status/2032860007272714396)

## Root cause

The heuristic told Claude to "check how long the current conversation has been running" and *guess* whether context was constrained. There's no actual token count API, so Claude erred on the side of caution and recommended compact-safe mode for any non-trivial conversation. Especially aggressive on Codex.

## What changed

Replaced the 35-line Phase 0 block (warning + choice prompt) with a 3-line default: always run full mode, compact-safe on explicit request only.

## Test plan

- [ ] Run `/ce:compound` in a fresh session — should go straight to full mode with no warning
- [ ] Run `/ce:compound` in a long session — should still go straight to full mode
- [ ] Run `/ce:compound --compact` — should use compact-safe mode
- [ ] Say "use compact mode" — should use compact-safe mode

## Post-Deploy Monitoring & Validation

No additional operational monitoring required: this is a prompt-only change with no runtime impact.

---

[![Compound Engineered](https://img.shields.io/badge/Compound-Engineered-6366f1)](https://github.com/EveryInc/compound-engineering-plugin) 🤖 Generated w

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
