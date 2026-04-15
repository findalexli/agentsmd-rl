# ty renders `/` and `*` parameter separators in wrong order for Callable types

## Problem

When ty displays a `Callable` type that has both positional-only parameters (indicated by `/`) and keyword-only parameters (indicated by `*`), the separators are rendered in the wrong order. For example, a callable like `def f(a, /, *, x, y) -> None` gets displayed as `(a, *, /, x, y) -> None` in type error messages instead of `(a, /, *, x, y) -> None`.

This produces syntactically invalid Python signatures in diagnostics. In Python, the `/` separator must always appear before the `*` separator — they delineate positional-only parameters and keyword-only parameters respectively, and positional-only must come first.

The issue occurs specifically when rendering `Callable` type signatures that combine both parameter kinds.

## Expected Behavior

The display of callable types should render the `/` separator before the `*` separator. For a callable with positional-only parameter `a` and keyword-only parameters `x, y`, the output should be `(a, /, *, x, y) -> None`.

Similarly, for multiple positional-only parameters followed by keyword-only: `(p, q, /, *, k) -> None`.

## Implementation Requirements

When displaying callable parameters, the `/` separator (indicating the end of positional-only parameters) must be emitted before the `*` separator (indicating the start of keyword-only parameters). This requires that within the loop body that iterates over `parameters` in the `FmtDetailed` implementation for `DisplayParameters`, the logic checking `parameter.is_positional_only()` must appear at an earlier source position than the logic checking `parameter.is_keyword_only()`. This source ordering ensures the separators appear in syntactically valid Python order.

Follow the development guidelines from `AGENTS.md`:
- Keep imports at the top of the file, not locally inside functions or impl blocks (AGENTS.md:76).
- Avoid `panic!` and `.unwrap()` — prefer encoding constraints in the type system or using proper error handling (AGENTS.md:79).
- If you must suppress a Clippy lint, prefer `#[expect()]` over `#[allow()]` where possible (AGENTS.md:81).

## Files to Look At

- `crates/ty_python_semantic/src/types/display.rs` — Contains the `FmtDetailed` implementation for `DisplayParameters`, which renders callable type parameter lists including the `/` and `*` separators.
