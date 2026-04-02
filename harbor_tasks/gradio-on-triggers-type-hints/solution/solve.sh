#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied (check for Trigger type alias in events.py)
grep -q 'Trigger = Union\[EventListenerCallable' gradio/events.py && exit 0

git apply - <<'PATCH'
diff --git a/gradio/events.py b/gradio/events.py
index 7086400018..abc3014b51 100644
--- a/gradio/events.py
+++ b/gradio/events.py
@@ -529,6 +529,10 @@ class EventListenerMethod:
         ],
         Dependency,
     ]
+    # Bound component event methods (e.g. button.click, tab.select) don't
+    # expose the ``block`` first-parameter present in EventListenerCallable,
+    # so we also accept any callable that returns a Dependency.
+    Trigger = Union[EventListenerCallable, Callable[..., Dependency]]


 class EventListener(str):
@@ -781,7 +785,7 @@ def inner(*args, **kwargs):

 @document()
 def on(
-    triggers: Sequence[EventListenerCallable] | EventListenerCallable | None = None,
+    triggers: Sequence[Trigger] | Trigger | None = None,
     fn: Callable[..., Any] | None | Literal["decorator"] = "decorator",
     inputs: Component
     | BlockContext
diff --git a/gradio/renderable.py b/gradio/renderable.py
index a5f334cb1c..b30b4ad9f1 100644
--- a/gradio/renderable.py
+++ b/gradio/renderable.py
@@ -13,7 +13,7 @@

 if TYPE_CHECKING:
     from gradio.blocks import BlockFunction
-    from gradio.events import EventListenerCallable
+    from gradio.events import Trigger


 class Renderable:
@@ -95,7 +95,7 @@ def apply(self, *args, **kwargs):
 @document()
 def render(
     inputs: Sequence[Component] | Component | None = None,
-    triggers: Sequence[EventListenerCallable] | EventListenerCallable | None = None,
+    triggers: Sequence[Trigger] | Trigger | None = None,
     *,
     queue: bool = True,
     trigger_mode: Literal["once", "multiple", "always_last"] | None = "always_last",

PATCH
