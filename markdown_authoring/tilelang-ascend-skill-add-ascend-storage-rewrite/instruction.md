# [skill] Add ascend storage rewrite design skill

Source: [tile-ai/tilelang-ascend#883](https://github.com/tile-ai/tilelang-ascend/pull/883)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/tilelang-pass-analyzer/ascend_storage_rewrite_design.md`

## What to add / change

This pull request adds a detailed design document for the `AscendStorageRewrite` pass, explaining its background, motivation, and the key changes made relative to the original TVM `StorageRewrite` pass. The document focuses on how the pass is integrated into the TileLang pipeline, the specific issues it addresses for Ascend vector operators, and the modifications made to ensure correctness and platform compatibility.

Key highlights from the design document:

**Background and Motivation:**
- Describes the migration of TVM's `StorageRewrite` to TileLang, emphasizing the need to prevent incorrect buffer reuse for different data types in Ascend vector scenarios.
- Explains why the original TVM reuse logic can cause semantic errors on Ascend, especially with dense temporary variables of mixed data types.

**Key Modifications for TileLang-Ascend:**
- Integration: The pass is now invoked as `tilelang.transform.AscendStorageRewrite(is_npu=...)` in the TileLang pipeline, replacing the generic TVM version.
- NPU Platform Handling: On NPU targets, aggressive allocation reuse is disabled to avoid high-risk buffer sharing across different data types.
- Annotation Preservation: Ensures that Ascend-specific annotations like `tl.local_var_init` are preserved through the rewrite process.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
