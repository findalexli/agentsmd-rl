#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

git apply - <<'PATCH'
diff --git a/gradio/cli/commands/skills.py b/gradio/cli/commands/skills.py
index a2e268d697..48ee9dff83 100644
--- a/gradio/cli/commands/skills.py
+++ b/gradio/cli/commands/skills.py
@@ -13,7 +13,7 @@
 import os
 import shutil
 from pathlib import Path
-from typing import Annotated
+from typing import Annotated, cast

 import typer
 from gradio_client import Client
@@ -187,7 +187,7 @@ def _generate_space_skill(space_id: str) -> tuple[str, str]:
             "Make sure the Space exists, is public (or provide HF_TOKEN), and is running."
         ) from e

-    api_info = client.view_api(print_info=False, return_format="dict")
+    api_info = cast(dict, client.view_api(print_info=False, return_format="dict"))
     src_url = client.src

     skill_id = _space_id_to_skill_id(space_id)
diff --git a/gradio/utils.py b/gradio/utils.py
index 233238034a..11840bdd95 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -1,7 +1,5 @@
 """Handy utility functions."""

-from __future__ import annotations
-
 import asyncio
 import copy
 import functools
@@ -152,7 +150,7 @@ def set(self, value: int):
 class BaseReloader(ABC):
     @property
     @abstractmethod
-    def running_app(self) -> App:
+    def running_app(self) -> "App":
         pass

     def get_attribute(self, attr: str, demo) -> Any:
@@ -166,7 +164,7 @@ def get_attribute(self, attr: str, demo) -> Any:
         else:
             return getattr(self.running_app.blocks, attr)

-    def swap_blocks(self, demo: Blocks):
+    def swap_blocks(self, demo: "Blocks"):
         assert self.running_app.blocks  # noqa: S101
         # Copy over the blocks to get new components and events but
         # not a new queue
@@ -222,7 +220,7 @@ def log(*args):
 class SpacesReloader(ServerReloader):
     def __init__(
         self,
-        app: App,
+        app: "App",
         watch_dirs: list[str],
         watch_module: ModuleType,
         stop_event: threading.Event,
@@ -238,7 +236,7 @@ def __init__(
         self._stop_event = stop_event

     @property
-    def running_app(self) -> App:
+    def running_app(self) -> "App":
         return self.app

     @property
@@ -257,7 +255,7 @@ def postrun(self, *_args, **_kwargs):
             return True
         return False

-    def swap_blocks(self, demo: Blocks):
+    def swap_blocks(self, demo: "Blocks"):
         super().swap_blocks(demo)
         demo.config = demo.get_config_file()

@@ -265,7 +263,7 @@ def swap_blocks(self, demo: Blocks):
 class SourceFileReloader(ServerReloader):
     def __init__(
         self,
-        app: App,
+        app: "App",
         watch_dirs: list[str],
         watch_module_name: str,
         demo_file: str,
@@ -286,7 +284,7 @@ def __init__(
         self.encoding = encoding

     @property
-    def running_app(self) -> App:
+    def running_app(self) -> "App":
         return self.app

     @property
@@ -300,7 +298,7 @@ def alert_change(self, change_type: Literal["reload", "error"] = "reload"):
         self.app.change_type = change_type
         self.app.change_count += 1

-    def swap_blocks(self, demo: Blocks):
+    def swap_blocks(self, demo: "Blocks"):
         old_blocks = self.running_app.blocks
         super().swap_blocks(demo)
         if old_blocks:
@@ -472,7 +470,7 @@ def _serialize(a: Any) -> bytes:
             return False


-def reassign_keys(old_blocks: Blocks, new_blocks: Blocks):
+def reassign_keys(old_blocks: "Blocks", new_blocks: "Blocks"):
     from gradio.blocks import Block, BlockContext

     new_keys = [
@@ -738,7 +736,7 @@ def resolve_singleton(_list: list[Any] | Any) -> Any:
         return _list


-def get_all_components() -> list[type[Component] | type[BlockContext]]:
+def get_all_components() -> "list[type[Component] | type[BlockContext]]":
     import gradio as gr

     classes_to_check = (
@@ -778,7 +776,7 @@ def core_gradio_components():
     ]


-def component_or_layout_class(cls_name: str) -> type[Component] | type[BlockContext]:
+def component_or_layout_class(cls_name: str) -> "type[Component] | type[BlockContext]":
     """
     Returns the component, template, or layout class with the given class name, or
     raises a ValueError if not found.
@@ -1049,11 +1047,11 @@ def wrapper(*args, **kwargs):

 def get_function_with_locals(
     fn: Callable,
-    blocks: Blocks,
+    blocks: "Blocks",
     event_id: str | None,
     in_event_listener: bool,
-    request: Request | None,
-    state: SessionState | None,
+    request: "Request | None",
+    state: "SessionState | None",
 ):
     def before_fn(blocks, event_id):
         from gradio.context import LocalContext
@@ -1945,9 +1943,9 @@ async def safe_aclose_iterator(iterator, timeout=60.0, retry_interval=0.05):


 def set_default_buttons(
-    buttons: Sequence[str | Button] | None = None,
+    buttons: "Sequence[str | Button] | None" = None,
     default_buttons: list[str] | None = None,
-) -> Sequence[str | Button]:
+) -> "Sequence[str | Button]":
     from gradio.components.button import Button

     if buttons is None:

PATCH
