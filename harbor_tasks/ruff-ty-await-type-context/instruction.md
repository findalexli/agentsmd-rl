# Bug: ty does not propagate type context through `await` expressions

## Summary

The `ty` type checker fails to propagate bidirectional type context through `await` expressions. This causes false positive `invalid-assignment` diagnostics when an async function returns a generic type (e.g., `list[Self]`) and the awaited result is assigned to a variable with a compatible annotation.

## Reproduction

```python
from typing import Self

class Parent:
    async def get_list(self) -> list[Self]:
        return [self]

    async def test(self):
        my_list: list[Parent] = await self.get_list()

class Child(Parent):
    async def func2(self):
        childs: list[Child] = await self.get_list()
```

Running `ty check` on this file incorrectly reports `invalid-assignment` errors on the `await` lines, because the type context from the left-hand-side annotation is not being forwarded through the `await` expression to inform inference of the call result.

A simpler example:

```python
from typing import Literal

async def make_lst[T](x: T) -> list[T]:
    return [x]

async def _():
    x: list[Literal[1]] = await make_lst(1)
```

Without the type context, `await make_lst(1)` infers as `list[int]`, which is not assignable to `list[Literal[1]]`.

## Relevant Code

The type inference dispatch for expressions is in:

- `crates/ty_python_semantic/src/types/infer/builder.rs`

Look at `infer_expression_impl` — this is the big match on `ast::Expr` variants. Many branches pass the `TypeContext` (`tcx`) parameter to their sub-inference methods (e.g., starred, dict, list expressions), but the `Await` variant currently does not forward the type context.

The `infer_await_expression` method itself is also in `builder.rs`. It needs to receive the type context and wrap it appropriately before passing it to the inner expression's inference.

## Expected Behavior

The type context should be propagated through `await` so that generic type inference can use the annotation on the left-hand side to narrow the awaited expression's type. The `invalid-assignment` false positives should disappear.
