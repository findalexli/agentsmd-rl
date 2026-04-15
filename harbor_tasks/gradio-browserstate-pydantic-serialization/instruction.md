# Fix BrowserState Pydantic model serialization

## Bug Description

`gr.BrowserState` incorrectly converts Pydantic `BaseModel` instances to their `str()` representation (e.g., `name='Dan' age=20`) instead of proper JSON-serializable dicts. This affects both the `default_value` parameter and the return values processed through `postprocess`.

The root cause is that when `BrowserState` stores a Pydantic model, it passes through `Block.get_config()` and then `ORJSONResponse` serialization. Since `orjson` cannot natively serialize Pydantic `BaseModel` instances, it falls back to `ORJSONResponse.default()` which calls `str(content)`, producing the Python repr string instead of a JSON-serializable dict.

For example, storing `Person(name="Dan", age=20)` results in the string `"name='Dan' age=20"` being stored in the browser's localStorage instead of `{"name": "Dan", "age": 20}`.

## Acceptance Criteria

- Pydantic `BaseModel` instances passed as `default_value` to `BrowserState` must be stored as dicts (e.g., `{"name": "Dan", "age": 20}`)
- Pydantic `BaseModel` instances returned from event handlers and processed by `BrowserState.postprocess()` must be converted to dicts
- Plain types (str, int, dict, list, bool, float, None) must pass through unchanged
- Nested Pydantic models must be recursively converted to nested dicts
- The file `gradio/components/browser_state.py` must remain syntactically valid Python
