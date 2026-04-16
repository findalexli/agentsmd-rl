# Fix filter_messages docstring example

## Problem

The `filter_messages` function in `libs/core/langchain_core/messages/utils.py` has a documentation bug in its docstring example. The example uses incorrect parameter names that don't match the actual function signature.

When users copy the example from the docstring and try to use it, they get a `TypeError` because the parameters shown don't exist.

## What you need to fix

Look at the docstring for `filter_messages` and find the code example. The example uses parameter names like `incl_names`, `incl_types`, and `excl_ids` - but the actual function parameters are named `include_names`, `include_types`, and `exclude_ids`.

Update the docstring example to use the correct full parameter names so that copying the example works correctly.

## Verification

Your fix should:
1. Allow the docstring example to run without raising `TypeError: filter_messages() got an unexpected keyword argument`
2. Make the example match the actual function signature

## Related files

- `libs/core/langchain_core/messages/utils.py` - Contains the `filter_messages` function that needs fixing
