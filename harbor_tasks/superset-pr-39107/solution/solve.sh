#!/bin/bash
# Gold solution for superset-mcp-truncation task
# Applies the fix from PR apache/superset#39107

set -e

cd /workspace/superset

# Check if patch was already applied (idempotency)
if grep -q "def _try_truncate_info_response" superset/mcp_service/middleware.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/superset/mcp_service/middleware.py b/superset/mcp_service/middleware.py
index b0ffc4f5f7c0..2254e8cc597c 100644
--- a/superset/mcp_service/middleware.py
+++ b/superset/mcp_service/middleware.py
@@ -936,6 +936,72 @@ def __init__(
             excluded_tools = [excluded_tools]
         self.excluded_tools = set(excluded_tools or [])

+    def _try_truncate_info_response(
+        self,
+        tool_name: str,
+        response: Any,
+        estimated_tokens: int,
+    ) -> Any | None:
+        """Attempt to dynamically truncate an info tool response to fit the limit.
+
+        Returns the truncated response if successful, None otherwise.
+        """
+        from superset.mcp_service.utils.token_utils import (
+            estimate_response_tokens,
+            truncate_oversized_response,
+        )
+
+        try:
+            truncated, was_truncated, notes = truncate_oversized_response(
+                response, self.token_limit
+            )
+        except (MemoryError, RecursionError) as trunc_error:
+            logger.warning(
+                "Truncation failed for %s due to %s: %s",
+                tool_name,
+                type(trunc_error).__name__,
+                trunc_error,
+            )
+            return None
+
+        if not was_truncated:
+            return None
+
+        truncated_tokens = estimate_response_tokens(truncated)
+        if truncated_tokens > self.token_limit:
+            return None
+
+        logger.warning(
+            "Response for %s truncated from ~%d to ~%d tokens (limit: %d). Fields: %s",
+            tool_name,
+            estimated_tokens,
+            truncated_tokens,
+            self.token_limit,
+            "; ".join(notes),
+        )
+
+        try:
+            user_id = get_user_id()
+            event_logger.log(
+                user_id=user_id,
+                action="mcp_response_truncated",
+                curated_payload={
+                    "tool": tool_name,
+                    "original_tokens": estimated_tokens,
+                    "truncated_tokens": truncated_tokens,
+                    "token_limit": self.token_limit,
+                    "truncation_notes": notes,
+                },
+            )
+        except Exception as log_error:  # noqa: BLE001
+            logger.warning("Failed to log truncation event: %s", log_error)
+
+        if isinstance(truncated, dict):
+            truncated["_response_truncated"] = True
+            truncated["_truncation_notes"] = notes
+
+        return truncated
+
     async def on_call_tool(
         self,
         context: MiddlewareContext,
@@ -984,9 +1050,18 @@ async def on_call_tool(

         # Block if over limit
         if estimated_tokens > self.token_limit:
-            # Extract params for smart suggestions
             params = getattr(context.message, "params", {}) or {}

+            # For info tools, try dynamic truncation before blocking
+            from superset.mcp_service.utils.token_utils import INFO_TOOLS
+
+            if tool_name in INFO_TOOLS:
+                truncated = self._try_truncate_info_response(
+                    tool_name, response, estimated_tokens
+                )
+                if truncated is not None:
+                    return truncated
+
             # Log the blocked response
             logger.error(
                 "Response blocked for %s: ~%d tokens exceeds limit of %d",
@@ -1011,9 +1086,6 @@ async def on_call_tool(
             except Exception as log_error:  # noqa: BLE001
                 logger.warning("Failed to log size exceeded event: %s", log_error)

-            # Generate helpful error message with suggestions
-            # Avoid passing the full `response` (which may be huge) into the formatter
-            # to prevent large-memory operations during error formatting.
             error_message = format_size_limit_error(
                 tool_name=tool_name,
                 params=params,
diff --git a/superset/mcp_service/utils/token_utils.py b/superset/mcp_service/utils/token_utils.py
index d4891634a8e6..423bbc6a224b 100644
--- a/superset/mcp_service/utils/token_utils.py
+++ b/superset/mcp_service/utils/token_utils.py
@@ -382,6 +382,210 @@ def _get_tool_specific_suggestions(
     return suggestions


+# Tools eligible for dynamic response truncation instead of hard blocking.
+# These tools return single objects (not paginated lists) where truncation
+# is preferable to returning an error.
+INFO_TOOLS = frozenset(
+    {
+        "get_chart_info",
+        "get_dataset_info",
+        "get_dashboard_info",
+        "get_instance_info",
+    }
+)
+
+# Maximum character length for string fields before truncation
+_MAX_STRING_CHARS = 500
+# Maximum items to keep in list fields before truncation
+_MAX_LIST_ITEMS = 30
+# Maximum keys to keep when summarizing large dict fields
+_MAX_DICT_KEYS = 20
+
+
+def _truncate_strings(
+    data: Dict[str, Any], notes: List[str], max_chars: int = _MAX_STRING_CHARS
+) -> bool:
+    """Truncate string fields exceeding max_chars at the top level only."""
+    changed = False
+    for key, value in data.items():
+        if isinstance(value, str) and len(value) > max_chars:
+            original_len = len(value)
+            data[key] = value[:max_chars] + f"... [truncated from {original_len} chars]"
+            notes.append(f"Field '{key}' truncated from {original_len} chars")
+            changed = True
+    return changed
+
+
+def _truncate_strings_recursive(
+    data: Any,
+    notes: List[str],
+    max_chars: int = _MAX_STRING_CHARS,
+    path: str = "",
+    _depth: int = 0,
+) -> bool:
+    """Recursively truncate strings throughout the entire data tree.
+
+    Walks nested dicts and list items to catch strings like
+    ``charts[0].description`` that top-level truncation misses.
+    Depth is capped at 10 to avoid runaway recursion.
+    """
+    if _depth > 10:
+        return False
+    changed = False
+    if isinstance(data, dict):
+        for key, value in data.items():
+            field_path = f"{path}.{key}" if path else key
+            if isinstance(value, str) and len(value) > max_chars:
+                original_len = len(value)
+                data[key] = (
+                    value[:max_chars] + f"... [truncated from {original_len} chars]"
+                )
+                notes.append(
+                    f"Field '{field_path}' truncated from {original_len} chars"
+                )
+                changed = True
+            elif isinstance(value, (dict, list)):
+                changed |= _truncate_strings_recursive(
+                    value, notes, max_chars, field_path, _depth + 1
+                )
+    elif isinstance(data, list):
+        for i, item in enumerate(data):
+            if isinstance(item, (dict, list)):
+                changed |= _truncate_strings_recursive(
+                    item, notes, max_chars, f"{path}[{i}]", _depth + 1
+                )
+    return changed
+
+
+def _truncate_lists(data: Dict[str, Any], notes: List[str], max_items: int) -> bool:
+    """Truncate list fields exceeding max_items. Returns True if any truncated.
+
+    Does NOT append marker objects into the list to preserve the element type
+    contract (e.g. ``List[TableColumnInfo]`` stays homogeneous).  Truncation
+    metadata is communicated through the *notes* list and top-level response
+    fields ``_response_truncated`` / ``_truncation_notes``.
+    """
+    changed = False
+    for key, value in data.items():
+        if isinstance(value, list) and len(value) > max_items:
+            original_len = len(value)
+            data[key] = value[:max_items]
+            notes.append(
+                f"Field '{key}' truncated from {original_len} to {max_items} items"
+            )
+            changed = True
+    return changed
+
+
+def _summarize_large_dicts(
+    data: Dict[str, Any], notes: List[str], max_keys: int = _MAX_DICT_KEYS
+) -> bool:
+    """Replace large dict fields with key summaries. Returns True if any changed."""
+    changed = False
+    for key, value in data.items():
+        if isinstance(value, dict) and len(value) > max_keys:
+            keys_list = list(value.keys())[:max_keys]
+            data[key] = {
+                "_truncated": True,
+                "_message": (
+                    f"Dict with {len(value)} keys truncated. "
+                    f"Keys: {', '.join(str(k) for k in keys_list)}..."
+                ),
+            }
+            notes.append(f"Field '{key}' dict summarized ({len(value)} keys)")
+            changed = True
+    return changed
+
+
+def _replace_collections_with_summaries(data: Dict[str, Any], notes: List[str]) -> bool:
+    """Replace all non-empty list/dict fields with empty/minimal values.
+
+    Lists are emptied (preserving the list type) rather than replaced with
+    marker objects to avoid breaking typed list contracts.
+    """
+    changed = False
+    for key, value in list(data.items()):
+        if not isinstance(value, (list, dict)) or not value:
+            continue
+        count = len(value)
+        if isinstance(value, list):
+            data[key] = []
+            notes.append(f"Field '{key}' list ({count} items) cleared to fit limit")
+        else:
+            data[key] = {}
+            notes.append(f"Field '{key}' dict ({count} keys) cleared to fit limit")
+        changed = True
+    return changed
+
+
+def _is_under_limit(data: Dict[str, Any], token_limit: int) -> bool:
+    """Check if the serialized data fits within the token limit."""
+    from superset.utils import json as utils_json
+
+    return estimate_token_count(utils_json.dumps(data)) <= token_limit
+
+
+def truncate_oversized_response(
+    response: ToolResponse,
+    token_limit: int,
+) -> tuple[ToolResponse, bool, list[str]]:
+    """
+    Dynamically truncate large fields in a response to fit within the token limit.
+
+    Applies five progressive phases of truncation:
+    1. Truncate long top-level string fields
+    2. Truncate large list fields to _MAX_LIST_ITEMS
+    3. Recursively truncate strings in nested structures (list items, nested dicts)
+    4. Aggressively reduce lists to 10 items and summarize large dicts
+    5. Replace all collections with empty values
+
+    Args:
+        response: The tool response (Pydantic model, dict, or other).
+        token_limit: Maximum estimated tokens allowed.
+
+    Returns:
+        A tuple of (possibly-truncated response, was_truncated, list of notes).
+    """
+    notes: list[str] = []
+
+    # Convert to a mutable dict for manipulation
+    if hasattr(response, "model_dump"):
+        data = response.model_dump()
+    elif isinstance(response, dict):
+        data = dict(response)
+    else:
+        return response, False, notes
+
+    was_truncated = False
+
+    # Phase 1: Truncate long string fields
+    was_truncated |= _truncate_strings(data, notes)
+    if _is_under_limit(data, token_limit):
+        return data, was_truncated, notes
+
+    # Phase 2: Truncate large list fields
+    was_truncated |= _truncate_lists(data, notes, _MAX_LIST_ITEMS)
+    if _is_under_limit(data, token_limit):
+        return data, was_truncated, notes
+
+    # Phase 3: Recursively truncate strings inside nested structures
+    # (e.g. charts[i].description, native_filters[i].config, etc.)
+    was_truncated |= _truncate_strings_recursive(data, notes)
+    if _is_under_limit(data, token_limit):
+        return data, was_truncated, notes
+
+    # Phase 4: Aggressively reduce lists and summarize large dicts
+    was_truncated |= _truncate_lists(data, notes, max_items=10)
+    was_truncated |= _summarize_large_dicts(data, notes)
+    if _is_under_limit(data, token_limit):
+        return data, was_truncated, notes
+
+    # Phase 5: Nuclear — replace all collections with empty values
+    was_truncated |= _replace_collections_with_summaries(data, notes)
+
+    return data, was_truncated, notes
+
+
 def format_size_limit_error(
     tool_name: str,
     params: Dict[str, Any] | None,
PATCH

echo "Gold patch applied successfully"
