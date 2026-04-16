# Task: Update Checkpoint Conformance Test Suite

## Problem

The `langgraph-checkpoint-conformance` package located at `libs/checkpoint-conformance/` provides a conformance test suite for LangGraph checkpointer implementations. One of its tests, `test_list_global_search` in the file `langgraph/checkpoint/conformance/spec/test_list.py`, requires cross-thread `alist(None, filter=...)` support. Not all checkpointer implementations can satisfy this requirement, causing them to fail conformance even though they are otherwise compliant.

A conformance test suite should only include tests that all valid implementations can pass. The `ALL_LIST_TESTS` list in the same file should contain exactly 16 test entries in its final state. The list must be consistent — every entry should reference a function that is defined in the module.

Additionally, the package version in `pyproject.toml` (currently `0.0.1`) should be updated to `0.0.2` to reflect this change.

## Constraints

- The test file must remain syntactically valid Python
- Other conformance tests must remain intact, including at minimum: `test_list_all`, `test_list_by_thread`, `test_list_ordering`, and `test_list_limit`
- All entries in `ALL_LIST_TESTS` must reference functions that are defined in the module
- Linting should pass

## Verification

After making changes, verify that:
- The test module can be imported without errors
- The `ALL_LIST_TESTS` list has the correct number of tests (16)
- The version in `pyproject.toml` is `0.0.2`
- Linting checks pass
