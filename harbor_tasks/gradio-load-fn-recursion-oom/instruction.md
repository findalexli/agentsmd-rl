# Bug: `gr.load` causes OOM / infinite recursion when loading HuggingFace models

## Summary

When using `gr.load()` to load a HuggingFace model (e.g. `gr.load("models/facebook/bart-large-cnn")`), the application crashes with an out-of-memory error or hits Python's recursion limit. The inference function ends up calling itself infinitely instead of calling the underlying HuggingFace pipeline.

## Reproduction

```python
import gradio as gr

demo = gr.load("models/facebook/bart-large-cnn", token="hf_...")
result = demo("Some text to summarize")
# -> RecursionError: maximum recursion depth exceeded
```

## Expected Behavior

- `gr.load()` should return a working `gr.Interface` that correctly delegates to the HuggingFace inference endpoint without recursion.
- The code should include a `kwargs.pop("fn", ...)` pattern to extract a function from keyword arguments.
- Error handling must satisfy all of the following:
  - `StopIteration` exceptions must be caught and converted to informative error messages (not leaked through).
  - Error messages for exceptions with no string representation (e.g., bare `Exception()`, `RuntimeError()`, `ValueError()`, `OSError()`) must be non-empty and contain the exception type name.
  - The error handler should contain at least 2 if-branches and at least 3 raise statements.
  - Errors containing "401" or "You must provide an api_key" must produce messages matching the regex `(?i)(unauthorized|signed in)`.
  - HTTP 429 errors must raise a `TooManyRequestsError`.
