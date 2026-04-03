# Improve API Info Display for File-Type Components

## Problem

When viewing API documentation for Gradio components that handle files (Image, Audio, File, etc.), the type information shown is a verbose, hard-to-read dict representation like:

```
dict(path: str | None, url: str | None, orig_name: str | None, mime_type: str | None, is_stream: bool, meta: dict(_type: ...))
```

This is confusing for users trying to understand the API — they just need to know they should provide a filepath.

Additionally, the Gradio CLI now supports `info` and `predict` commands (via the `hf-gradio` extension) for interacting with Gradio apps and Spaces programmatically. These are particularly useful for coding agents that need to discover endpoints and send predictions. The project's agent skill documentation should be updated to cover these commands.

## Expected Behavior

1. **API info display**: File-type schemas (those with a `path` property and `meta` containing `gradio.FileData`) should display as simply `filepath` instead of the full dict representation. Non-file objects should continue showing the dict format.

2. **Skill documentation**: The `.agents/skills/gradio/SKILL.md` file should document the new CLI prediction commands so that coding agents know how to use them.

## Files to Look At

- `client/python/gradio_client/utils.py` — contains `_json_schema_to_python_type` which converts JSON schemas to human-readable Python type strings. The logic for `type == "object"` needs to detect file schemas and return `"filepath"` early.
- `.agents/skills/gradio/SKILL.md` — the agent skill file that documents how to use Gradio. Should be updated to document the `gradio info` and `gradio predict` CLI commands, including usage examples.
