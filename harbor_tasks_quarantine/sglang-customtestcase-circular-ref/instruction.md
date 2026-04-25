# Bug: dill serialization emits recursive-reference warnings for CustomTestCase subclasses

## Summary

When using `dill.dumps()` on subclasses of `CustomTestCase` (defined in `python/sglang/test/test_utils.py`), serialization emits warnings about recursive self-references, indicating a circular reference exists in the class hierarchy. Fix `CustomTestCase` so that this circular reference is eliminated.

## Observed symptom

Calling `dill.dumps()` on a `CustomTestCase` subclass that defines `setUpClass` produces warnings containing the string `"recursive self-references"`. For example:

```python
import dill, warnings

class MyTest(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        pass
    def test_example(self):
        pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    dill.dumps(MyTest)

# w contains warnings with "recursive self-references" in the message
```

This indicates a circular reference cycle involving the subclass and its wrapped `setUpClass` method.

## Requirements

After fixing, all of the following must hold:

1. **No dill warning**: `dill.dumps()` on a `CustomTestCase` subclass must not emit any warnings whose message contains `"recursive self-references"`.

2. **No circular reference in function defaults**: Inspecting `SubclassOfCustomTestCase.setUpClass.__func__.__defaults__` must not reveal any bound method whose `__self__` attribute references the subclass. Specifically, for each default value `d`, if `hasattr(d, "__self__")` is true, then `d.__self__` must not be the subclass class itself.

3. **Original setUpClass still invoked**: The safety wrapping must still correctly invoke the original `setUpClass` implementation. When `setUpClass` raises an exception, `tearDownClass` must still be called (best-effort cleanup).

4. **No double-wrapping**: Subclasses of subclasses of `CustomTestCase` must not double-wrap `setUpClass`. The `_safe_setup_wrapped` attribute is used to guard against re-wrapping. Calling `setUpClass` on a grandchild class should invoke the original `setUpClass` exactly once.

5. **Meaningful `__init_subclass__`**: The `CustomTestCase.__init_subclass__` method must retain meaningful logic (at least 3 non-docstring statements). Do not stub it out or remove it.

6. **Code quality**: The modified file must pass `ruff` (syntax `E9` and import `F401,F821` checks), `black --check`, `isort --check`, `codespell`, and pre-commit hooks (`check-ast`, `trailing-whitespace`, `end-of-file-fixer`, `debug-statements`).

## File to modify

- `python/sglang/test/test_utils.py`
