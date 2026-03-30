# Fix UP008 nested class matching

## Bug Description

The UP008 rule (`super-call-with-parameters`) incorrectly triggers inside nested classes when the `super()` call references the inner class name. In Python, this would actually be a `NameError` at runtime because the inner class name is not in scope.

For example, this should NOT trigger UP008:

```python
class Outer:
    class Inner(Base):
        def method(self):
            super(Inner, self).__init__()  # Inner is not in scope here -- NameError!
```

The current implementation finds the enclosing class by walking up the statement parents, but it does not verify that the class name used in the `super()` call actually resolves to the correct nesting level. When there are multiple levels of class nesting, it incorrectly matches the inner class name even though that name is not accessible at runtime.

Similarly, for dotted access like `super(Inner.C, self)`, the implementation needs to verify that the entire chain of class names matches the enclosing class nesting, and that there are no additional outer classes that would make the name unreachable.

The existing fixture file has `TODO(charlie)` comments marking these as known false positives.

## Files to Modify

- `crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs`
- `crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py` (remove TODO comments)
