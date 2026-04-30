# claude: update skills on hugging face reference

Source: [flashinfer-ai/flashinfer-bench#174](https://github.com/flashinfer-ai/flashinfer-bench/pull/174)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-reference-tests/SKILL.md`
- `.claude/skills/extract-kernel-definitions/SKILL.md`
- `CLAUDE.md`

## What to add / change

On new kernel definitions, refer to HF on model-specific constants, refer to SGL on runtime-specific constants.

#173 

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Clarified that HuggingFace model config is the primary source for model constants, with SGLang used for runtime-specific values.
  * Reorganized guidance on locating and verifying kernel/reference implementations, emphasizing FlashInfer tests first and SGLang as a fallback.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
