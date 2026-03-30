# Fix BrowserState Pydantic model serialization

## Bug Description

`gr.BrowserState` incorrectly converts Pydantic `BaseModel` instances to their `str()` representation (e.g., `name='Dan' age=20`) instead of proper JSON-serializable dicts. This affects both the `default_value` parameter in `__init__` and the return values processed through `postprocess`.

The root cause is that when `BrowserState` stores a Pydantic model, it passes through `Block.get_config()` and then `ORJSONResponse` serialization. Since `orjson` cannot natively serialize Pydantic `BaseModel` instances, it falls back to `ORJSONResponse.default()` which calls `str(content)`, producing the Python repr string instead of a JSON-serializable dict.

For example, storing `Person(name="Dan", age=20)` results in the string `"name='Dan' age=20"` being stored in the browser's localStorage instead of `{"name": "Dan", "age": 20}`.

## What to Fix

In `gradio/components/browser_state.py`:

1. Add a helper function that converts Pydantic `BaseModel` instances to dicts via `model_dump()`, passing through all other values unchanged.
2. Apply this conversion in `__init__` when storing `default_value`, so that Pydantic models used as default values are properly serialized.
3. Apply this conversion in `postprocess` when processing return values from event handlers, so that Pydantic models returned by user functions are properly serialized.

## Affected Code

- `gradio/components/browser_state.py`: `BrowserState.__init__()` and `BrowserState.postprocess()`

## Acceptance Criteria

- Pydantic `BaseModel` instances passed as `default_value` are stored as dicts
- Pydantic `BaseModel` instances returned from event handlers are converted to dicts in `postprocess`
- Plain types (str, int, dict, None) are passed through unchanged
- Nested Pydantic models are properly converted
- The file remains syntactically valid Python
