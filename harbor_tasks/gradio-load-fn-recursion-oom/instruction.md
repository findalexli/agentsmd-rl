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

## Relevant Files

- `gradio/external.py` — The `from_model()` function constructs an inference wrapper and then builds a `gr.Interface` from it. The wrapper closure captures a variable from its enclosing scope, but that variable gets reassigned later in the same scope, causing the closure to call itself recursively.

- `gradio/external_utils.py` — The `handle_hf_error()` function doesn't handle `StopIteration` exceptions (raised when no inference provider supports the model). It also produces empty error messages when an exception has no string representation.

## Expected Behavior

- `gr.load()` should return a working `gr.Interface` that correctly delegates to the HuggingFace inference endpoint without recursion.
- Error messages from unsupported models should be informative, not empty strings.
