# Fix Callable type display ordering for positional-only and keyword-only parameters

## Problem

When displaying a `Callable` type that combines both positional-only parameters (indicated by `/`) and keyword-only parameters (indicated by `*`), the separators are rendered in the wrong order.

For example, a callable with positional-only parameter `a` and keyword-only parameters `x, y` currently displays as `(a, *, /, x, y) -> None` instead of the syntactically correct `(a, /, *, x, y) -> None`.

Similarly, for multiple positional-only parameters `p, q` followed by keyword-only parameter `k`, the output should be `(p, q, /, *, k) -> None`.

In Python, the `/` separator (end of positional-only) must always appear before the `*` separator (start of keyword-only). The current display produces syntactically invalid Python signatures in type error messages.

## Expected Behavior

When both `/` and `*` separators are needed in callable type display, the `/` separator must appear before the `*` separator.

The following exact output strings must be produced for the corresponding callable signatures:
- `(a, /, *, x, y) -> None` — for a callable with positional-only `a` and keyword-only `x, y`
- `(p, q, /, *, k) -> None` — for a callable with positional-only `p, q` and keyword-only `k`

The display logic involves iterating over parameters using a loop pattern `for parameter in parameters`. The methods `parameter.is_positional_only()` and `parameter.is_keyword_only()` are used to determine when to emit the `/` and `*` separators. Currently, the check for keyword-only parameters occurs too early in the display loop, causing the `*` separator to be emitted before the `/` separator.

## Implementation Requirements

Follow the development guidelines from `AGENTS.md`:
- Keep imports at the top of the file, not locally inside functions or impl blocks (AGENTS.md:76).
- Avoid `panic!` and `.unwrap()` — prefer encoding constraints in the type system or using proper error handling (AGENTS.md:79).
- If you must suppress a Clippy lint, prefer `#[expect()]` over `#[allow()]` where possible (AGENTS.md:81).
