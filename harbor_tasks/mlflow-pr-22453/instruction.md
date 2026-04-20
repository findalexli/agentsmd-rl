# Task: Handle Gemini SDK Bytes Repr in inline_data Extraction

## Symptom

When a span's `set_outputs` or `set_inputs` receives a Gemini-format dictionary containing an `inline_data` field with `data` holding a **Python `repr(bytes)` string** (e.g., `"b'\\x89PNG...'"`), the following problems occur:

1. The `data` value is **not rewritten** to an `mlflow-attachment://` reference.
2. No attachment is stored in `span._attachments`.
3. The original byte content is lost — subsequent code that expects `span._attachments` to contain the decoded bytes finds it empty.

## Expected Behavior

When `inline_data` contains a Python bytes repr string (detected by the `"b'"` or `'b"'` prefix), the extraction code should:

1. Parse the repr string back into a `bytes` object.
2. Store it as an `mlflow-attachment://` reference in the span's outputs/inputs.
3. Register it in `span._attachments` with the correct `content_type` (e.g., `"image/png"`, `"audio/wav"`).
4. Return the same result as if the data had been base64-encoded.

## Example Failure

```python
span = _make_live_span()
bytes_repr = repr(png_bytes)  # e.g., "b'\\x89PNG...'"
span.set_outputs({
    "candidates": [{
        "content": {
            "parts": [
                {"text": "A small image."},
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": bytes_repr,
                    }
                },
            ]
        }
    }]
})

# PROBLEM: data stays as raw repr string, no attachment created
parts = span.outputs["candidates"][0]["content"]["parts"]
assert parts[1]["inline_data"]["data"].startswith("mlflow-attachment://")  # FAILS
assert len(span._attachments) == 1  # FAILS
```

## Context

- **Source**: Gemini SDK uses Pydantic models internally. When those models serialize a `bytes` field to JSON, it uses Python's `repr()` format rather than base64. The MLflow span extraction code encounters this format when tracing Gemini SDK calls.
- **File**: `mlflow/entities/span.py` — specifically the `inline_data` extraction path in `_try_convert_structured_content`.
- **Related existing tests**: `tests/entities/test_span_auto_extract_attachments.py::test_extracts_gemini_inline_data` (base64 variant) and `test_gemini_inline_data_with_invalid_base64` (error case) provide reference patterns.
