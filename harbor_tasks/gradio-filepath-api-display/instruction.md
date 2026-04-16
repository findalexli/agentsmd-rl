# Improve API Info Display for File-Type Components

## Problem

When viewing API documentation for Gradio components that handle files (Image, Audio, File, etc.), the type information shown is a verbose, hard-to-read dict representation like:

```
dict(path: str | None, url: str | None, orig_name: str | None, mime_type: str | None, is_stream: bool, meta: dict(_type: ...))
```

This is confusing for users trying to understand the API — they just need to know they should provide a filepath.

## Target Function

The function `gradio_client.utils._json_schema_to_python_type` converts JSON schemas to human-readable Python type strings. This is the function that must be updated to handle file-type schemas.

## Expected Behavior

File-type JSON schemas should display as simply `filepath` instead of the full dict representation. Non-file objects should continue showing the dict format.

A file-type schema has these characteristics:
- Contains a `path` property (typically with `anyOf` allowing string or null)
- Has a `meta` property where either:
  - The `meta` definition contains `_type` with `const: "gradio.FileData"` (resolved via `$ref` to `$defs/Meta`), OR
  - The `meta` property has a `default` dict containing `"_type": "gradio.FileData"`
- Uses `$defs` to define the `Meta` schema structure

When such a schema is detected, the display should return the literal string `"filepath"`. For nested file schemas within other objects, the outer structure should still show as `dict(...)` but with the file field rendered as `filepath`.

For plain objects without file characteristics (no `path` property, no `gradio.FileData` meta), continue displaying as `dict(...)` with the property names.

The helper function `value_is_file` in `gradio_client.utils` should also correctly identify whether a schema represents a file type for API info purposes.
