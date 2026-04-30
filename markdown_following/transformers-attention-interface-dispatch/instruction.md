# Align Latest Model Attention Function Dispatch

The `ALL_ATTENTION_FUNCTIONS` global in `transformers.modeling_utils` provides a centralized `get_interface()` method for dispatching attention implementations. However, some recently added models still use a manual dispatch pattern that bypasses this centralized method, leaving them inconsistent with the rest of the codebase.

## Symptom

In certain model attention forward methods, the attention function dispatch looks like this:

```python
attention_interface = eager_attention_forward
if self.config._attn_implementation != "eager":
    attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
```

This manual pattern does three things differently from the centralized approach:
1. It does not validate that `_attn_implementation` is a registered key — valid implementations like `"sdpa"` or `"flash_attention_2"` are in the registry; names not in the registry (e.g. `nonexistent_impl_xyz_test`) raise `KeyError`
2. It does not handle `None` gracefully — returns `eager_attention_forward` with a warning instead of raising `KeyError`
3. It duplicates dispatch logic that should live in one place

Other models in the codebase already use the centralized `get_interface()` method from the `AttentionInterface` class (instantiated as `ALL_ATTENTION_FUNCTIONS` in `src/transformers/modeling_utils.py`). The `get_interface()` method takes two arguments: the attention implementation name and a default callable to return when the implementation is `"eager"` or `None`.

## What to do

Find the model attention forward methods that still use the manual `_attn_implementation != "eager"` dispatch pattern and update them to use `ALL_ATTENTION_FUNCTIONS.get_interface()` instead.

For models that have both a `modular_*.py` file and a `modeling_*.py` file, both files need to be updated consistently.

In `modular_*.py` files that use the `Callable` type hint without importing it, add `from collections.abc import Callable`.

## Code Style Requirements

Run `ruff check --ignore UP038` on any files you modify. The `UP038` ruff rule targets a pre-existing issue unrelated to this task and should be ignored. The code must pass style checks with this ignore flag.

## Verification

After making your changes, verify:
- All attention forward methods that previously used the manual dispatch now call `get_interface()`
- The old `_attn_implementation != "eager"` pattern no longer appears in the affected attention forward methods
- `ruff check` passes on modified files
