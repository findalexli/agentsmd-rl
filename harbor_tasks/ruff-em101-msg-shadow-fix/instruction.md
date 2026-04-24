# Task: Fix missing utility function in Gradio

When external tools attempt to access a certain utility function in `gradio.utils`, an `AttributeError` is raised because this attribute does not exist in the `gradio.utils` module.

## Expected behavior

The `gradio.utils` module should expose a callable function that retrieves the machine's interface IP address. The function should:

- Be a callable function (not a constant or class).
- Have a docstring explaining its purpose.
- When called with no arguments, return a string representing a valid IPv4 address in dotted-decimal notation (e.g., `"192.168.1.10"`).
  - The returned string must match the pattern `x.x.x.x` where each `x` is an integer from 0 to 255.
  - The function must not return `None`.

## Verification requirements

After your changes:
- The function in `gradio.utils` should be accessible via `hasattr(gradio.utils, '<function_name>')`
- The function should have a docstring
- Calling the function with no arguments must return a non-None string matching a valid IPv4 address with four octets each in the range 0–255
- Running `python -m ruff format --check` and `python -m ruff check --select E9,E1,F` on the modified code must pass (return code 0)
- All existing gradio package imports and basic functionality must continue working

## Constraints

- Do not remove or rename any existing functions in the `gradio.utils` module
- Do not break existing imports or basic functionality of the gradio package
- Ensure the modified code passes ruff formatting and lint checks
