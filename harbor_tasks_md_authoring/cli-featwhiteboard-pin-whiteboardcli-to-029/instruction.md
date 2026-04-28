# feat(whiteboard): Pin whiteboard-cli to ^0.2.9

Source: [larksuite/cli#617](https://github.com/larksuite/cli/pull/617)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-whiteboard/SKILL.md`
- `skills/lark-whiteboard/references/lark-whiteboard-update.md`
- `skills/lark-whiteboard/references/layout.md`
- `skills/lark-whiteboard/references/schema.md`
- `skills/lark-whiteboard/routes/dsl.md`
- `skills/lark-whiteboard/routes/mermaid.md`
- `skills/lark-whiteboard/routes/svg.md`
- `skills/lark-whiteboard/scenes/bar-chart.md`
- `skills/lark-whiteboard/scenes/fishbone.md`
- `skills/lark-whiteboard/scenes/flywheel.md`
- `skills/lark-whiteboard/scenes/line-chart.md`
- `skills/lark-whiteboard/scenes/treemap.md`

## What to add / change

## Summary
<!-- Briefly describe the motivation and scope of this change in 1-3 sentences. -->

## Changes
Update whiteboard-cli to ^0.2.9


## Related Issues
<!-- Link related issues. Use Closes/Fixes to close them automatically. -->
- None


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Updated Lark Whiteboard CLI version references from ^0.2.0 to ^0.2.9 across all skill documentation, examples, and guides.
  * Simplified environment verification instructions: removed earlier pre-check steps and consolidated checks into the streamlined command-based validation flow.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
