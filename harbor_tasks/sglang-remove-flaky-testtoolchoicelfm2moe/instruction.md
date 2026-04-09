# Remove flaky TestToolChoiceLfm2Moe test class

## Problem

The `TestToolChoiceLfm2Moe` test class in the SGLang test suite is flaky and unreliable. This test class uses the `LiquidAI/LFM2-8B-A1B` model for testing tool choice functionality, but this model is not reliable for tool calling, causing CI failures.

The flaky tests were originally marked in the `flaky_tests` set:
- `test_multi_tool_scenario_auto`
- `test_multi_tool_scenario_required`

Rather than maintaining a flaky test that provides little value (the same `lfm2` parser logic is already covered by `TestToolChoiceLfm2` and unit tests in `test_function_call_parser.py`), the test class should be removed entirely.

## Expected Behavior

The `TestToolChoiceLfm2Moe` class should be completely removed from the test file. All other test classes must remain intact.

## Files to Look At

- `test/registered/openai_server/function_call/test_tool_choice.py` — This file contains multiple test classes for tool choice functionality. The `TestToolChoiceLfm2Moe` class (lines ~891-918) should be removed while preserving all other classes like `TestToolChoiceLlama32`, `TestToolChoiceLfm2`, `TestToolChoiceQwen25`, and `TestToolChoiceMistral`.

## Notes

- The class to remove starts with `class TestToolChoiceLfm2Moe(TestToolChoiceLlama32):`
- The class uses model `"LiquidAI/LFM2-8B-A1B"` and parser `"lfm2"`
- The file should end with `if __name__ == "__main__":` followed by `unittest.main()` on the same indent level after removal
- Make sure not to break the file structure (imports, other classes, main guard)
