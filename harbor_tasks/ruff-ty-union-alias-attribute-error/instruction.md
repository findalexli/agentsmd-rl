# ty fails to report attribute errors through type-aliased unions

## Bug description

When a union type is expressed through a `type` alias (PEP 695), ty's attribute-error
diagnostics do not properly descend into the alias to identify which concrete union
members are missing the attribute. Instead of reporting which specific types lack the
attribute, the error is either missing or incorrectly formed.

## Reproduction

```python
class A:
    pass

class B:
    def do_b_thing(self) -> None:
        pass

type U = A | B

class C:
    def __init__(self, values: list[U]) -> None:
        self.values = values

    def f(self) -> None:
        for item in self.values:
            item.do_b_thing()   # should warn: A has no `do_b_thing`
```

Running `ty check` on this file should emit an `unresolved-attribute` diagnostic
indicating that `A` does not define `do_b_thing`. Currently, the diagnostic machinery
only inspects the top-level union elements without unwrapping union-like types (type
aliases that resolve to unions, `NewType`s, etc.), so the individual concrete types
inside the alias are never checked.

## Relevant code

The attribute-resolution logic lives in
`crates/ty_python_semantic/src/types/infer/builder.rs`, in the section that handles
`ExprAttribute` nodes. When the value type is a union, the code collects elements
missing the requested attribute — but it does not recurse into union-like elements
(e.g., type aliases that themselves expand to unions).

## Expected behavior

`ty check` should correctly identify that `A` lacks `do_b_thing` and emit:

```
error[unresolved-attribute]: Attribute `do_b_thing` is not defined on `A` in union `Unknown | U`
```
