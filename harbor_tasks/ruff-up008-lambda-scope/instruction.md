# Fix UP008 callable scope handling to support lambdas

## Bug Description

The UP008 rule (`super-call-with-parameters`) in ruff does not detect `super()` calls with unnecessary parameters inside lambda expressions defined as class body attributes. For example:

```python
class LambdaMethod(BaseClass):
    f = lambda self: super(LambdaMethod, self).f()
```

This lambda uses `super(LambdaMethod, self)` which can be simplified to `super()`, just like a regular method. However, the current implementation only checks `Function` scopes, not `Lambda` scopes. As a result, this valid simplification is missed.

The rule's scope-checking logic needs to be extended to also recognize `Lambda` scopes (and `DunderClassCell` scopes that may wrap them) as valid callable contexts for the UP008 check. The parameter extraction logic also needs to handle lambda parameter lists, which have a different AST structure than function definitions.

The existing fixture file already has a test case for this with a `TODO(charlie)` comment indicating the case is known to be missed.

## Files to Modify

- `crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs`
- `crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py` (remove TODO comment)
