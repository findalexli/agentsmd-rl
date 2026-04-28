# add copilot-instructions.md

Source: [OpenCCU/OpenCCU#3656](https://github.com/OpenCCU/OpenCCU/pull/3656)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Expanded developer docs with end-to-end guidance on repository layout, supported build targets, and primary build/release commands.
  * Added detailed patching conventions and workflows (patch generation/regeneration rules and CI divergence behavior), plus kernel/defconfig and DTS expectations.
  * Documented CI checks, release artifact patterns, add-on/config synchronization, nested recovery-system build design including 32-bit multilib handling, custom package sources, and contributor best practices.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
