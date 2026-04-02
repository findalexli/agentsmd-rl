#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if __getattr__ already exists in html.py, skip
if grep -q '__getattr__' gradio/components/html.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/components/html.py b/gradio/components/html.py
index 2a6a8154d8..d2a9f28d07 100644
--- a/gradio/components/html.py
+++ b/gradio/components/html.py
@@ -6,6 +6,7 @@
 import re
 import textwrap
 from collections.abc import Callable, Sequence
+from functools import partial
 from typing import TYPE_CHECKING, Any, Literal, cast

 from gradio_client.documentation import document
@@ -13,7 +14,7 @@
 from gradio.blocks import BlockContext
 from gradio.components.base import Component, server
 from gradio.components.button import Button
-from gradio.events import all_events
+from gradio.events import EventListener, all_events
 from gradio.i18n import I18nData
 from gradio.utils import set_default_buttons

@@ -189,6 +190,18 @@ def get_config(self) -> dict[str, Any]:  # type: ignore[override]
         config["component_class_name"] = self.component_class_name
         return config

+    def __getattr__(self, name: str):
+        js = self.__dict__.get("js_on_load") or ""
+        pattern = rf"""(?:['"`]){re.escape(name)}(?:['"`])"""
+        if re.search(pattern, js):
+            trigger = EventListener(event_name=name)
+            return partial(trigger.listener, self)
+        raise AttributeError(
+            f"'{type(self).__name__}' object has no attribute '{name}'. "
+            f"If '{name}' is a custom event, make sure to include '{name}' "
+            f"(enclosed in quotes) in the js_on_load string."
+        )
+
     def get_block_name(self):
         return "html"

PATCH

echo "Patch applied successfully."
