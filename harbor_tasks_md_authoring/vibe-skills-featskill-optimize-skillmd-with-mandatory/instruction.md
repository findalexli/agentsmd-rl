# feat(skill): optimize SKILL.md with mandatory router intent extraction (v3.1.0)

Source: [foryourhealth111-pixel/Vibe-Skills#193](https://github.com/foryourhealth111-pixel/Vibe-Skills/pull/193)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

- **New top section**: `Mandatory Router Invocation With Intent Optimization` -- forces AI to explicitly call the canonical router at vibe entry, with mandatory keyword text extraction rules (not raw prompts) to improve router intent hit rate
- **Streamlined Canonical Bootstrap**: removed POSIX command block, consolidated Hard Rules from 8 to 4, merged Bootstrap steps
- **Removed redundant sections**: What vibe Does, Runtime Mode, Compatibility With Process Layers, Learn And Retro Surface, Memory Rules (merged into other sections)
- **Fixed auto-promote ambiguity**: changed to "MUST be promoted" language
- **Rewritten Router section**: `Router Invocation At Entry` now references the mandatory intent extraction rules
- **Streamlined sections**: Internal Execution Grades, Stage Contract, Quality Rules, Known Boundaries
- **Version bump**: 3.0.4 -> 3.1.0
- **Line reduction**: 398 -> 241 (39%)

## Test plan

- [ ] Verify vibe still enters canonical governed runtime correctly
- [ ] Verify router call behavior unchanged (intent extraction is an AI-level instruction, not a runtime change)
- [ ] Verify all 6 stages still fire in order
- [ ] Review English-only content in the document


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

## Release Notes

* **Documentation**
  * Updated skill activation routing requirements and mandated router invocation before runtime stages
  * Added router input protocol 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
