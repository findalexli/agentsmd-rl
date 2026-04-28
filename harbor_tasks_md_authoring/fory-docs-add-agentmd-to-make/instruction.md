# docs: add AGENT.md to make AI coding more efficient

Source: [apache/fory#2646](https://github.com/apache/fory/pull/2646)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Why?

Add CLAUDE.md to make AI coding more efficient, CLAUDE.md will make ai coding with any models more easy

## What does this PR do?
Add CLAUDE.md 

## Related issues

This document is inspired by https://github.com/apache/opendal/blob/main/CLAUDE.md

cc @Xuanwo 

## Does this PR introduce any user-facing change?

<!--
If any user-facing interface changes, please [open an issue](https://github.com/apache/fory/issues/new/choose) describing the need to do so and update the document if necessary.

Delete section if not applicable.
-->

- [ ] Does this PR introduce any public API change?
- [ ] Does this PR introduce any binary protocol compatibility change?

## Benchmark

<!--
When the PR has an impact on performance (if you don't know whether the PR will have an impact on performance, you can submit the PR first, and if it will have impact on performance, the code reviewer will explain it), be sure to attach a benchmark data here.

Delete section if not applicable.
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
