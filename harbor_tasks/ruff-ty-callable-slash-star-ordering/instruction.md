# ty renders `/` and `*` parameter separators in wrong order for Callable types

## Problem

When ty displays a `Callable` type that has both positional-only parameters (indicated by `/`) and keyword-only parameters (indicated by `*`), the separators are rendered in the wrong order. For example, a callable like `def f(a, /, *, x, y) -> None` gets displayed as `(a, *, /, x, y) -> None` in type error messages instead of `(a, /, *, x, y) -> None`.

This produces syntactically invalid Python signatures in diagnostics. In Python, the `/` separator must always appear before the `*` separator — they delineate positional-only parameters and keyword-only parameters respectively, and positional-only must come first.

The issue occurs specifically when rendering `Callable` type signatures that combine both parameter kinds.

## Expected Behavior

The display of callable types should render the `/` separator before the `*` separator. For a callable with positional-only parameter `a` and keyword-only parameters `x, y`, the output should be `(a, /, *, x, y) -> None`.

Similarly, for multiple positional-only parameters followed by keyword-only: `(p, q, /, *, k) -> None`.

## Files to Look At

- `crates/ty_python_semantic/src/types/display.rs` — Contains the `FmtDetailed` implementation for `DisplayParameters`, which renders callable type parameter lists including the `/` and `*` separators.
