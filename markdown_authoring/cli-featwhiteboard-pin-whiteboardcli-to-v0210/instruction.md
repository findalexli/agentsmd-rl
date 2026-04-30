# feat(whiteboard): pin whiteboard-cli to v0.2.10 in lark-whiteboard skill

Source: [larksuite/cli#649](https://github.com/larksuite/cli/pull/649)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-whiteboard/SKILL.md`
- `skills/lark-whiteboard/references/content.md`
- `skills/lark-whiteboard/references/image.md`
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
- `skills/lark-whiteboard/scenes/photo-showcase.md`
- `skills/lark-whiteboard/scenes/treemap.md`

## What to add / change

## Summary
<!-- Briefly describe the motivation and scope of this change in 1-3 sentences. -->

## Changes
feat(whiteboard): pin whiteboard-cli to v0.2.10 in lark-whiteboard skill

## Related Issues
<!-- Link related issues. Use Closes/Fixes to close them automatically. -->
- None


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Chores**
  * Updated whiteboard CLI version references across documentation.

* **New Features**
  * Image nodes now require whiteboard-scoped media tokens and uploads to the target board.

* **Documentation**
  * Rewrote Image Preparation workflow: download, validate, upload, verify; forbids placeholder services.
  * Removed keyword-triggered image insertion and legacy image+text card guidance; expanded post-render validation and deduplication checks.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
