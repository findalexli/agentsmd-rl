# Fix create_grammar_backend test calls with think_end_id parameter

## Problem

The unit tests in `test/registered/unit/constrained/test_base_grammar_backend.py` for the `create_grammar_backend` factory function are broken. Several tests in the `TestCreateGrammarBackend` class that verify reasoner wrapping behavior are failing because they use an outdated calling convention.

The tests currently set `tokenizer.think_end_id = 42` on the mock tokenizer object, but `create_grammar_backend` no longer reads `think_end_id` from the tokenizer — it now accepts it as an explicit keyword argument. Because the parameter is not passed, it defaults to `None`, causing the reasoner wrapping tests to fail.

Affected test methods:
- `test_custom_backend_skips_reasoner_wrapping`
- `test_reasoner_wrapping_on_builtin_backend`
- `test_no_reasoner_wrapping_without_think_end_id`
- `test_no_reasoner_wrapping_without_reasoning_parser`

## Expected Behavior

The tests should call `create_grammar_backend(args, tokenizer, vocab_size, think_end_id=42)` (or `think_end_id=None` where appropriate) and should NOT set `tokenizer.think_end_id` as a mock attribute.

## Files to Look At

- `test/registered/unit/constrained/test_base_grammar_backend.py` — the unit test file with outdated API calls
- `python/sglang/srt/constrained/base_grammar_backend.py` — contains `create_grammar_backend` with the updated function signature
