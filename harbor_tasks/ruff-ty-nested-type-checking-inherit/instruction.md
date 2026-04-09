# [ty] Nested conditional blocks don't inherit TYPE_CHECKING state

## Problem

When using `typing.TYPE_CHECKING` with nested conditional blocks, ty's type checker incorrectly emits `invalid-overload` diagnostics for overloaded functions that should be treated as stub-like declarations.

For example, overloaded functions directly inside `if TYPE_CHECKING:` are correctly recognized as stub-like (no implementation required). But if there's an additional conditional nested inside the `TYPE_CHECKING` block — such as `if sys.platform == "win32": ... else: @overload ...` — ty fails to recognize that the inner block is still within a `TYPE_CHECKING` context. This causes false `invalid-overload` errors complaining about missing implementation functions.

The issue affects any nesting pattern: `if/else`, `elif`, and even deeper nesting levels within `TYPE_CHECKING` blocks.

## Expected Behavior

Nested conditional clauses inside `if TYPE_CHECKING:` blocks should inherit the `TYPE_CHECKING` state from the outer block. Overloaded functions inside these nested blocks should not produce `invalid-overload` diagnostics, matching the behavior for overloads directly inside `TYPE_CHECKING`.

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index/builder.rs` — The semantic index builder where `in_type_checking_block` state is managed during AST visitation
