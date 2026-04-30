# Remove @export recommendations from godot-task skill

Source: [htdt/godogen#1](https://github.com/htdt/godogen/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/godot-task/SKILL.md`

## What to add / change

The generator now decides when to use @export on its own, so prescriptive
guidance about exporting all tunable parameters is no longer needed.

Removed:
- "Scene @export Parameters" section and examples
- "Script @export Parameters" section and examples
- @export vars from scene and script templates
- "Exposes ALL tuneable parameters via @export" from script requirements
- "exports" from script section ordering
- @export from movement pattern examples

The GDScript syntax reference (gdscript.md) retains @export documentation
since that's language reference, not a recommendation.

https://claude.ai/code/session_01ParLabdhoV1ok4hhrwoPMV

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
