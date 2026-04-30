# docs(guideline): ✂️ trim duplicated cloudbase guidance

Source: [TencentCloudBase/CloudBase-MCP#504](https://github.com/TencentCloudBase/CloudBase-MCP/pull/504)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `config/source/guideline/cloudbase/SKILL.md`

## What to add / change

Summary: trim the cloudbase guideline quick reference, remove the duplicated Platform-Specific Skills block, and compress behavior rules plus console entry sections without changing routing semantics or build scripts. Verification: build-allinone completed successfully; skill-activation-routing tests passed; build-allinone tests remained skipped by environment gate. Scope: source-only change in config/source/guideline/cloudbase/SKILL.md with no edits to activation-map.yaml, build scripts, or publishing workflows.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
