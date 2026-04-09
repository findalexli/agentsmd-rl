#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if grep -q 'find_tool_properties' vllm/tool_parsers/qwen3coder_tool_parser.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/tool_parsers/qwen3coder_tool_parser.py b/vllm/tool_parsers/qwen3coder_tool_parser.py
index ea25ea2be923..7b089ceffbc0 100644
--- a/vllm/tool_parsers/qwen3coder_tool_parser.py
+++ b/vllm/tool_parsers/qwen3coder_tool_parser.py
@@ -25,6 +25,7 @@
     Tool,
     ToolParser,
 )
+from vllm.tool_parsers.utils import find_tool_properties

 logger = init_logger(__name__)

@@ -109,28 +110,6 @@ def _reset_streaming_state(self):
         self.accumulated_params = {}
         self.streaming_request = None

-    def _get_arguments_config(self, func_name: str, tools: list[Tool] | None) -> dict:
-        """Extract argument configuration for a function."""
-        if tools is None:
-            return {}
-        for config in tools:
-            if not hasattr(config, "type") or not (
-                hasattr(config, "function") and hasattr(config.function, "name")
-            ):
-                continue
-            if config.type == "function" and config.function.name == func_name:
-                if not hasattr(config.function, "parameters"):
-                    return {}
-                params = config.function.parameters
-                if isinstance(params, dict) and "properties" in params:
-                    return params["properties"]
-                elif isinstance(params, dict):
-                    return params
-                else:
-                    return {}
-        logger.debug("Tool '%s' is not defined in the tools list.", func_name)
-        return {}
-
     def _convert_param_value(
         self, param_value: str, param_name: str, param_config: dict, func_name: str
     ) -> Any:
@@ -243,16 +222,14 @@ def _convert_param_value(
                 )
             return param_value

-    def _parse_xml_function_call(
-        self, function_call_str: str, tools: list[Tool] | None
-    ) -> ToolCall | None:
+    def _parse_xml_function_call(self, function_call_str: str) -> ToolCall | None:
         # Extract function name
         end_index = function_call_str.find(">")
         # If there's no ">" character, this is not a valid xml function call
         if end_index == -1:
             return None
         function_name = function_call_str[:end_index]
-        param_config = self._get_arguments_config(function_name, tools)
+        param_config = find_tool_properties(self.tools, function_name)
         parameters = function_call_str[end_index + 1 :]
         param_dict = {}
         for match_text in self.tool_call_parameter_regex.findall(parameters):
@@ -314,7 +291,7 @@ def extract_tool_calls(
                 )

             tool_calls = [
-                self._parse_xml_function_call(function_call_str, self.tools)
+                self._parse_xml_function_call(function_call_str)
                 for function_call_str in function_calls
             ]
             # Populate prev_tool_call_arr for serving layer to set finish_reason
@@ -605,9 +582,8 @@ def extract_tool_calls_streaming(
                 self.current_param_name = current_param_name
                 self.accumulated_params[current_param_name] = param_value

-                param_config = self._get_arguments_config(
-                    self.current_function_name or "",
-                    self.tools,
+                param_config = find_tool_properties(
+                    self.tools, self.current_function_name or ""
                 )

                 converted_value = self._convert_param_value(
@@ -666,7 +642,6 @@ def extract_tool_calls_streaming(
                     try:
                         parsed_tool = self._parse_xml_function_call(
                             func_content,
-                            self.tools,
                         )
                         if parsed_tool and self.current_tool_index < len(
                             self.prev_tool_call_arr
diff --git a/vllm/tool_parsers/qwen3xml_tool_parser.py b/vllm/tool_parsers/qwen3xml_tool_parser.py
index 6e28c82b13d9..4ecb9666886f 100644
--- a/vllm/tool_parsers/qwen3xml_tool_parser.py
+++ b/vllm/tool_parsers/qwen3xml_tool_parser.py
@@ -26,6 +26,7 @@
     Tool,
     ToolParser,
 )
+from vllm.tool_parsers.utils import find_tool_properties

 logger = init_logger(__name__)

@@ -1000,33 +1001,11 @@ def _get_param_type(self, param_name: str) -> str:
         if not self.tools or not self.current_function_name:
             return "string"

-        for tool in self.tools:
-            if not hasattr(tool, "type") or not (
-                hasattr(tool, "function") and hasattr(tool.function, "name")
-            ):
-                continue
-            if (
-                tool.type == "function"
-                and tool.function.name == self.current_function_name
-            ):
-                if not hasattr(tool.function, "parameters"):
-                    return "string"
-                params = tool.function.parameters
-                if isinstance(params, dict) and "properties" in params:
-                    properties = params["properties"]
-                    if param_name in properties and isinstance(
-                        properties[param_name], dict
-                    ):
-                        return self.repair_param_type(
-                            str(properties[param_name].get("type", "string"))
-                        )
-                elif isinstance(params, dict) and param_name in params:
-                    param_config = params[param_name]
-                    if isinstance(param_config, dict):
-                        return self.repair_param_type(
-                            str(param_config.get("type", "string"))
-                        )
-                break
+        properties = find_tool_properties(self.tools, self.current_function_name)
+        if param_name in properties and isinstance(properties[param_name], dict):
+            return self.repair_param_type(
+                str(properties[param_name].get("type", "string"))
+            )
         return "string"

     def repair_param_type(self, param_type: str) -> str:
diff --git a/vllm/tool_parsers/utils.py b/vllm/tool_parsers/utils.py
index 82b7eaaab209..b25198924b35 100644
--- a/vllm/tool_parsers/utils.py
+++ b/vllm/tool_parsers/utils.py
@@ -142,6 +142,20 @@ def _extract_tool_info(
         raise TypeError(f"Unsupported tool type: {type(tool)}")


+def find_tool_properties(
+    tools: list[Tool] | None,
+    tool_name: str,
+) -> dict[str, Any]:
+    """Find a tool by name and return its properties dict, or {}."""
+    if not tools:
+        return {}
+    for tool in tools:
+        name, params = _extract_tool_info(tool)
+        if name == tool_name:
+            return (params or {}).get("properties", {})
+    return {}
+
+
 def _get_tool_schema_from_tool(tool: Tool) -> dict:
     name, params = _extract_tool_info(tool)
     params = params if params else {"type": "object", "properties": {}}

PATCH

echo "Patch applied successfully."
