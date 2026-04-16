# MCP Info Tool Response Size Issue

## Problem

The MCP (Model Context Protocol) service in Superset has a `ResponseSizeGuardMiddleware` that blocks responses exceeding a configured token limit. When info tools (`get_chart_info`, `get_dataset_info`, `get_dashboard_info`, `get_instance_info`) return responses that exceed this limit, the middleware currently returns an error to the client.

This is problematic because info tools return single objects with no pagination option, and responses can be very large (dashboards with hundreds of charts, datasets with many columns, charts with large `form_data`).

## Task

Modify the MCP service to dynamically truncate oversized info tool responses instead of blocking them. Add truncation utility functions to `superset/mcp_service/utils/token_utils.py` and integrate them into the `ResponseSizeGuardMiddleware` in `superset/mcp_service/middleware.py`.

## Requirements

### 1. INFO_TOOLS constant

Define a module-level `INFO_TOOLS` constant as a `frozenset` containing exactly these four tool names:

- `get_chart_info`
- `get_dataset_info`
- `get_dashboard_info`
- `get_instance_info`

### 2. Default truncation thresholds

Define module-level constants for default thresholds:

- `_MAX_STRING_CHARS = 500` — max characters for string fields
- `_MAX_LIST_ITEMS = 30` — max items to keep in list fields
- `_MAX_DICT_KEYS = 20` — max keys to keep before summarizing dict fields

### 3. Helper functions in token_utils.py

All helper functions take a `notes: List[str]` argument that they append descriptive messages to when truncation occurs, and return `bool` indicating whether any changes were made.

#### `_truncate_strings(data, notes, max_chars=_MAX_STRING_CHARS) -> bool`

Truncates string values in `data` (a `Dict[str, Any]`) exceeding `max_chars` at the **top level only**. Each truncated string is replaced with its first `max_chars` characters followed by the marker:

```
... [truncated from {original_len} chars]
```

where `{original_len}` is the original character count. For each truncated field, append a note like `"Field 'description' truncated from 1000 chars"`. The parameter controlling the character limit must be named `max_chars`.

#### `_truncate_strings_recursive(data, notes, max_chars=_MAX_STRING_CHARS, path="", _depth=0) -> bool`

Recursively truncates strings throughout nested dicts and lists. Uses dot-separated paths in notes, for example when truncating `data["charts"][0]["description"]` the note should contain `"charts[0].description"`. Recursion depth is capped at 10 to prevent stack overflow. The parameter controlling the character limit must be named `max_chars`.

#### `_truncate_lists(data, notes, max_items) -> bool`

Truncates list values in `data` (a `Dict[str, Any]`) exceeding `max_items` by slicing (keeps the first `max_items` elements). Does **not** append marker objects into the list — this preserves list type contracts (e.g., `List[TableColumnInfo]` stays homogeneous). The parameter controlling the item limit must be named `max_items`.

#### `_summarize_large_dicts(data, notes, max_keys=_MAX_DICT_KEYS) -> bool`

Replaces dict values in `data` with more than `max_keys` entries with a summary dict containing exactly these two keys:

- `"_truncated"`: `True`
- `"_message"`: a string like `"Dict with 30 keys truncated. Keys: key_0, key_1, ..."` listing up to `max_keys` of the original keys

The parameter controlling the key limit must be named `max_keys`.

#### `_replace_collections_with_summaries(data, notes) -> bool`

Replaces all non-empty list fields with `[]` and all non-empty dict fields with `{}`. Scalar values and already-empty collections remain unchanged.

### 4. Main orchestrator function

#### `truncate_oversized_response(response, token_limit) -> tuple`

Returns a 3-tuple: `(possibly_truncated_response, was_truncated: bool, notes: list[str])`.

- Converts the response to a mutable dict (handles Pydantic models via `model_dump()` and plain dicts via `dict()` copy)
- Non-dict/model responses (e.g., strings) are returned unchanged with `(response, False, [])`
- Applies five progressive phases of truncation, checking the token count after each phase via `_is_under_limit(data, token_limit)`:
  1. `_truncate_strings` — truncate long top-level string fields
  2. `_truncate_lists` with `_MAX_LIST_ITEMS` — truncate large list fields
  3. `_truncate_strings_recursive` — recursively truncate strings in nested structures
  4. `_truncate_lists` with `max_items=10` **and** `_summarize_large_dicts` — aggressively reduce lists and summarize large dicts
  5. `_replace_collections_with_summaries` — replace all collections with empty values (nuclear fallback)
- If at any point the data fits within the token limit, returns early with the current state

### 5. Middleware integration

In `ResponseSizeGuardMiddleware.on_call_tool`, when a response exceeds the token limit and the tool name is in `INFO_TOOLS`, attempt truncation via `truncate_oversized_response` before falling back to the error response. If truncation succeeds and the result fits within the limit, return the truncated response. On the truncated response dict, add these two metadata keys:

- `"_response_truncated"`: `True`
- `"_truncation_notes"`: the list of truncation notes returned by the orchestrator

### 6. Quality requirements

- Both modified files must pass `ruff check` (linting) and `ruff format --check` (formatting)
- Existing functions `estimate_token_count`, `estimate_response_tokens`, and `CHARS_PER_TOKEN` must continue to work correctly
