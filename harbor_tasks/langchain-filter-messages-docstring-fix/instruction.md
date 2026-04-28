# Fix filter_messages docstring example

## Problem

The `filter_messages` function in `langchain_core.messages.utils` has a docstring with an Example section containing runnable code. When users copy and paste this example, they receive a `TypeError` about an unexpected keyword argument.

The function's signature accepts keyword arguments including `include_names`, `include_types`, and `exclude_ids`. However, the docstring example currently passes abbreviated parameter names — `incl_names`, `incl_types`, and `excl_ids` — which the function does not recognize. This mismatch causes `TypeError: got an unexpected keyword argument` at runtime.

## What you need to do

Update the docstring example for `filter_messages` so that users can copy and run it without encountering a `TypeError`. The example should use parameter names consistent with the function's signature.

Look at the function's signature in the source code to confirm the correct keyword argument names, then fix the docstring example accordingly. Do not change the function implementation or any logic outside the docstring.

## Code Style Requirements

This project enforces code style with `ruff`. Your changes must pass `ruff check` on the modified file. Run the linter before considering your work complete.

## Verification

After your fix:
1. The docstring example runs without raising `TypeError` or `unexpected keyword argument` errors
2. The example uses parameter names matching the function's actual signature
3. `ruff check` passes on the modified file
4. No function behavior or logic is changed — only the docstring example is corrected
