#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q '_is_file_schema' client/python/gradio_client/utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/gradio/SKILL.md b/.agents/skills/gradio/SKILL.md
index e4c7bfb5efd..78a53d584c6 100644
--- a/.agents/skills/gradio/SKILL.md
+++ b/.agents/skills/gradio/SKILL.md
@@ -158,6 +158,59 @@ with gr.Blocks() as demo:
 demo.launch()
 ```

+## Prediction CLI
+
+The `gradio` CLI includes `info` and `predict` commands for interacting with Gradio apps programmatically. These are especially useful for coding agents that need to use Spaces in their workflows.
+
+### `gradio info` — Discover endpoints and parameters
+
+```bash
+gradio info <space_id_or_url>
+```
+
+Returns a JSON payload describing all endpoints, their parameters (with types and defaults), and return values.
+
+```bash
+gradio info gradio/calculator
+#    {
+#   "/predict": {
+#     "parameters": [
+#       {"name": "num1", "required": true, "default": null, "type": {"type": "number"}},
+#       {"name": "operation", "required": true, "default": null, "type": {"enum": ["add", "subtract", "multiply", "divide"], "type": "string"}},
+#       {"name": "num2", "required": true, "default": null, "type": {"type": "number"}}
+#     ],
+#     "returns": [{"name": "output", "type": {"type": "number"}}],
+#     "description": ""
+#   }
+# }
+```
+
+File-type parameters show `"type": "filepath"` with instructions to include `"meta": {"_type": "gradio.FileData"}` — this signals the file will be uploaded to the remote server.
+
+### `gradio predict` — Send predictions
+
+```bash
+gradio predict <space_id_or_url> <endpoint> <json_payload>
+```
+
+Returns a JSON object with named output keys.
+
+```bash
+# Simple numeric prediction
+gradio predict gradio/calculator /predict '{"num1": 5, "operation": "multiply", "num2": 3}'
+# {"output": 15}
+
+# Image generation
+gradio predict black-forest-labs/FLUX.2-dev /infer '{"prompt": "A majestic dragon"}'
+# {"Result": "/tmp/gradio/.../image.webp", "Seed": 1117868604}
+
+# File upload (must include meta key)
+gradio predict gradio/image_mod /predict '{"image": {"path": "/path/to/image.png", "meta": {"_type": "gradio.FileData"}}}'
+# {"output": "/tmp/gradio/.../output.png"}
+```
+
+Both commands accept `--token` for accessing private Spaces.
+
 ## Event Listeners

 All event listeners share the same signature:
diff --git a/client/python/gradio_client/utils.py b/client/python/gradio_client/utils.py
index 9277099fc8d..ab1e7967e71 100644
--- a/client/python/gradio_client/utils.py
+++ b/client/python/gradio_client/utils.py
@@ -960,12 +960,13 @@ def _json_schema_to_python_type(schema: Any, defs) -> str:
             elements = _json_schema_to_python_type(items, defs)
             return f"list[{elements}]"
     elif type_ == "object":
+        props = schema.get("properties", {})
+        if _is_file_schema(schema, defs or {}):
+            return "filepath"

         def get_desc(v):
             return f" ({v.get('description')})" if v.get("description") else ""

-        props = schema.get("properties", {})
-
         des = [
             f"{n}: {_json_schema_to_python_type(v, defs)}{get_desc(v)}"
             for n, v in props.items()
@@ -1160,8 +1161,54 @@ async def async_traverse(


 def value_is_file(api_info: dict) -> bool:
-    info = _json_schema_to_python_type(api_info, api_info.get("$defs"))
-    return any(file_data_format in info for file_data_format in FILE_DATA_FORMATS)
+    return _schema_contains_file(api_info, api_info.get("$defs", {}))
+
+
+def _resolve_ref(schema: dict, defs: dict) -> dict:
+    """Resolve a $ref to its definition."""
+    if "$ref" in schema:
+        ref_name = schema["$ref"].split("/")[-1]
+        if ref_name in defs:
+            return defs[ref_name]
+    return schema
+
+
+def _is_file_schema(schema: dict, defs: dict | None = None) -> bool:
+    """Check if a schema directly represents a file type (has path + meta with gradio.FileData)."""
+    if defs is None:
+        defs = schema.get("$defs", {})
+    props = schema.get("properties", {})
+    if "path" not in props or "meta" not in props:
+        return False
+    meta = _resolve_ref(props["meta"], defs)
+    meta_props = meta.get("properties", {})
+    if "_type" in meta_props:
+        type_schema = meta_props["_type"]
+        return type_schema.get("const") == "gradio.FileData"
+    meta_default = meta.get("default", {})
+    if isinstance(meta_default, dict):
+        return meta_default.get("_type") == "gradio.FileData"
+    return False
+
+
+def _schema_contains_file(schema, defs: dict) -> bool:
+    """Recursively check if a JSON schema contains a file type anywhere."""
+    if not isinstance(schema, dict):
+        if isinstance(schema, list):
+            return any(_schema_contains_file(item, defs) for item in schema)
+        return False
+    if "$ref" in schema:
+        ref_name = schema["$ref"].split("/")[-1]
+        if ref_name in defs:
+            return _schema_contains_file(defs[ref_name], defs)
+        return False
+    if _is_file_schema(schema, defs):
+        return True
+    return any(
+        _schema_contains_file(v, defs)
+        for k, v in schema.items()
+        if k != "$defs" and isinstance(v, (dict, list))
+    )


 def is_filepath(s) -> bool:

PATCH

echo "Patch applied successfully."
