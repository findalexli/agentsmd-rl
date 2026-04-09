# Queue validation response handling ignores invalid dict responses

## Problem

In `gradio/queueing.py`, the `process_validation_response` function does not correctly handle validation responses that arrive as a single dictionary (rather than a list). When a validator returns a dict like `{"is_valid": False, "message": "Input out of range"}`, the function silently treats it as valid and returns `all_valid=True`. This means invalid inputs are never rejected when the validation response is a dict.

## Expected Behavior

When `process_validation_response` receives a dict with `is_valid` set to `False`, it should return `all_valid=False` and include the invalid response in the returned `validation_data` list.

## Files to Look At

- `gradio/queueing.py` — Contains the `process_validation_response` function that processes validation results from event handlers
