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

Similarly, for dotted access like `super(Inner.C, self)` with extra outer nesting, the implementation needs to verify that the entire chain of class names matches the enclosing class nesting. For example, given:

```python
class HigherLevelsOfNesting:
    class Inner:
        class C(Base):
            def __init__(self, foo):
                super(Inner.C, self).__init__(foo)
```

This should NOT trigger UP008 because `Inner.C` is not fully resolvable from within `C.__init__` (the `Inner` part would need to be accessed through the outer class scope).

Conversely, when the dotted chain matches the full class nesting exactly, UP008 should still trigger:

```python
class A:
    class B:
        class C(Base):
            def __init__(self, foo):
                super(A.B.C, self).__init__(foo)  # This SHOULD trigger UP008
```

Regular top-level super calls should continue to trigger UP008:

```python
class MyClass(Base):
    def __init__(self, foo):
        super(MyClass, self).__init__(foo)  # This SHOULD trigger UP008
```

The fixture file contains TODO comments with the text "false positive until nested class matching is fixed" that must be removed once the fix is implemented.

## Files to Modify

- `crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs`
- `crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py` (remove TODO comments about nested class false positives)

## Coding Standards (per AGENTS.md)

When modifying the Rust code, follow these constraints:

1. **No panic patterns**: Do not use `.unwrap()`, `panic!()`, or `unreachable!()` in the rule file. Use safe error handling with `if let` or `let...else` instead.

2. **Imports at top**: All `use` statements must be at the top of the file, never locally inside function bodies.

3. **Prefer let chains**: When checking multiple conditions with `if let`, combine them with `&&` (let chains) instead of using nested `if let` blocks. For example:
   - Preferred: `if let Some(a) = x && let Some(b) = y { ... }`
   - Avoid: nested `if let` statements

4. **Clippy suppressions**: If suppressing a Clippy lint, use `#[expect(...)]` instead of `#[allow(...)]`.
