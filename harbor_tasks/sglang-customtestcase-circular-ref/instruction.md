# Bug: dill serialization fails for classes defined inside CustomTestCase subclasses

## Summary

When using `dill.dumps()` on classes that are defined inside test methods of `CustomTestCase` subclasses (in `python/sglang/test/test_utils.py`), serialization emits recursive-reference warnings and may fail for classes defined within those test methods.

## Expected behavior

After the fix, the following must all be true:

1. **No dill warning**: `dill.dumps(SubclassOfCustomTestCase)` must not emit "recursive self-references" warnings.
2. **No circular reference**: The wrapping mechanism must not create a reference cycle through bound-method defaults. Specifically, the wrapped `setUpClass` function must not capture the original bound method as a default parameter that holds a reference back to the class (via `__self__`).
3. **Original still called**: The wrapped `setUpClass` must still invoke the original `setUpClass` implementation.
4. **Normal subclass behavior**: Subclasses of subclasses must not double-wrap; `setUpClass` must be called exactly once.

## Files involved

- `python/sglang/test/test_utils.py` — the `CustomTestCase` class with its `__init_subclass__` hook
