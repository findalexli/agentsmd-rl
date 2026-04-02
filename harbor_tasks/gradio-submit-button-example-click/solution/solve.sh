#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied
grep -q 'example_select_runs' gradio/chat_interface.py && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/gradio/chat_interface.py b/gradio/chat_interface.py
index 529b6a0626..c1e96b3fe0 100644
--- a/gradio/chat_interface.py
+++ b/gradio/chat_interface.py
@@ -626,12 +626,14 @@ def _setup_events(self) -> None:
         )

         example_select_event = None
+        example_select_runs = False
         if (
             isinstance(self.chatbot, Chatbot)
             and self.examples
             and not self._additional_inputs_in_examples
         ):
             if self.cache_examples or self.run_examples_on_click:
+                example_select_runs = True
                 example_select_event = self.chatbot.example_select(
                     self.example_clicked,
                     None,
@@ -639,6 +641,21 @@ def _setup_events(self) -> None:
                     api_visibility="undocumented",
                 )
                 if not self.cache_examples:
+                    textbox_component = (
+                        MultimodalTextbox if self.multimodal else Textbox
+                    )
+                    example_select_event = example_select_event.then(
+                        utils.async_lambda(
+                            lambda: textbox_component(
+                                submit_btn=False,
+                                stop_btn=self.original_stop_btn,
+                            )
+                        ),
+                        None,
+                        [self.textbox],
+                        api_visibility="undocumented",
+                        queue=False,
+                    )
                     example_select_event = example_select_event.then(**submit_fn_kwargs)
                 example_select_event.then(**synchronize_chat_state_kwargs)
             else:
@@ -678,13 +695,12 @@ def _setup_events(self) -> None:
         ).then(**save_fn_kwargs)

         events_to_cancel = [submit_event, retry_event]
-        if example_select_event is not None:
+        if example_select_event is not None and example_select_runs:
             events_to_cancel.append(example_select_event)

         self._setup_stop_events(
             event_triggers=[
                 self.chatbot.retry,
-                self.chatbot.example_select,
             ],
             events_to_cancel=events_to_cancel,
             after_success=user_submit,

PATCH
