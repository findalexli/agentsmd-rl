# add claude skills

Source: [ROCm/FlyDSL#244](https://github.com/ROCm/FlyDSL/pull/244)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/bisect-perf-regression/SKILL.md`
- `.claude/skills/build-flydsl/SKILL.md`
- `.claude/skills/build-rocm-image/SKILL.md`
- `.claude/skills/debug-flydsl-kernel/SKILL.md`
- `.claude/skills/flydsl-kernel-authoring/SKILL.md`
- `.claude/skills/format-code/SKILL.md`
- `.claude/skills/gemm-optimization/SKILL.md`
- `.claude/skills/lds-optimization/SKILL.md`
- `.claude/skills/prefetch-data-load/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Motivation

<!-- Explain the purpose of this PR and the goals it aims to achieve. -->

## Technical Details

<!-- Explain the changes along with any relevant GitHub links. -->

## Test Plan

<!-- Explain any relevant testing done to verify this PR. -->

## Test Result

<!-- Briefly summarize test outcomes. -->

## Submission Checklist

- [ ] Look over the contributing guidelines at https://github.com/ROCm/ROCm/blob/develop/CONTRIBUTING.md#pull-requests.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
