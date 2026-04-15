# Fix create_grammar_backend test calls for think_end_id parameter

## Problem

The unit tests in `test/registered/unit/constrained/test_base_grammar_backend.py` for the `create_grammar_backend` factory function are broken. Several tests in the `TestCreateGrammarBackend` class that verify reasoner wrapping behavior are failing.

The tests set `tokenizer.think_end_id = 42` as a mock attribute, but `create_grammar_backend` no longer reads this from the tokenizer — the parameter must now be passed explicitly. Because it is not passed, it defaults to `None`, causing the reasoner wrapping tests to fail.

## Expected Behavior

For each affected test method, the `create_grammar_backend` call must pass `think_end_id` as an explicit keyword argument. Additionally, any `tokenizer.think_end_id = N` assignments in the affected methods must be removed — the mock attribute is no longer read by the function.

## Affected Test Methods

The following four test methods in `TestCreateGrammarBackend` need to be updated:

- `test_custom_backend_skips_reasoner_wrapping`
- `test_reasoner_wrapping_on_builtin_backend`
- `test_no_reasoner_wrapping_without_think_end_id`
- `test_no_reasoner_wrapping_without_reasoning_parser`

## Files to Look At

- `test/registered/unit/constrained/test_base_grammar_backend.py` — the unit test file
- `python/sglang/srt/constrained/base_grammar_backend.py` — contains `create_grammar_backend` with the updated function signature