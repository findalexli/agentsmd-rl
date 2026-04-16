# Task: Fix missing utility function in Gradio

When external tools attempt to access `gradio.utils.get_interface_ip`, an `AttributeError` is raised because this attribute does not exist in the `gradio.utils` module.

## Expected behavior

The `gradio.utils` module should expose a callable function named `get_interface_ip` with the following requirements:

- It must be a callable function (not a constant or class).
- It must have a non-None docstring (`__doc__` must not be `None`).
- When called with no arguments, it must return a string representing a valid IPv4 address in dotted-decimal notation (e.g., `"192.168.1.10"`).
  - The returned string must match the pattern `x.x.x.x` where each `x` is an integer from 0 to 255.
  - The function must not return `None`.

## Verification requirements

After your changes:
- `import gradio.utils; hasattr(gradio.utils, 'get_interface_ip')` must be `True`
- `gradio.utils.get_interface_ip.__doc__` must not be `None`
- `gradio.utils.get_interface_ip()` must return a non-None string matching a valid IPv4 address with four octets each in the range 0–255
- Running `python -m ruff format --check` and `python -m ruff check --select E9,E1,F` on the modified code must pass (return code 0)
- All existing gradio package imports and basic functionality must continue working

## Constraints

- Do not remove or rename any existing functions in the `gradio.utils` module
- Do not break existing imports or basic functionality of the gradio package
- Ensure the modified code passes ruff formatting and lint checks
