# chore(whiteboard): Manual disable edge case for svg compatible

Source: [larksuite/cli#661](https://github.com/larksuite/cli/pull/661)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-whiteboard/references/lark-whiteboard-update.md`
- `skills/lark-whiteboard/routes/svg.md`

## What to add / change

## Summary
<!-- Briefly describe the motivation and scope of this change in 1-3 sentences. -->

## Changes
Manual disable edge case for svg compatible

## Related Issues
<!-- Link related issues. Use Closes/Fixes to close them automatically. -->
- None


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Clarified SVG guidance: decorative SVG features (gradients, filters, patterns, clipping/masking) are unsupported in whiteboard conversion, can cause rendering issues, and should be avoided; guidance updated to emphasize balancing editability and appearance.
  * Corrected terminology in diagram-type guidance from “图标” to “图表” for recommended diagrams (mind maps, sequence/class diagrams, pie charts, flowcharts, etc.).
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
