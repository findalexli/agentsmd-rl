#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency: check if already applied
if grep -q '_append_message_to_history' gradio/chat_interface.py | grep -c 'self.chatbot.edit' 2>/dev/null; then
    true  # fall through to check
fi

# Check for the specific fix marker: _append_message_to_history chained after edit
if python3 -c "
import ast, sys
src = open('gradio/chat_interface.py').read()
# If the fix is applied, 'saved_input' appears near the edit block with append_message
# A simple heuristic: count occurrences of _append_message_to_history
count = src.count('_append_message_to_history')
# Buggy code has 5 occurrences, fixed code has 6
sys.exit(0 if count >= 6 else 1)
" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/chat_interface.py b/gradio/chat_interface.py
index c1e96b3fe0..208f5001ab 100644
--- a/gradio/chat_interface.py
+++ b/gradio/chat_interface.py
@@ -737,9 +737,21 @@ def _setup_events(self) -> None:
                 [self.chatbot],
                 [self.chatbot, self.chatbot_state, self.saved_input],
                 api_visibility="undocumented",
+            ).then(
+                self._append_message_to_history,
+                [self.saved_input, self.chatbot_state],
+                [self.chatbot],
+                api_visibility="undocumented",
+                queue=False,
+            ).success(
+                lambda: update(interactive=False),
+                outputs=[self.textbox],
+                api_visibility="undocumented",
             ).success(**submit_fn_kwargs).success(**synchronize_chat_state_kwargs).then(
-                **save_fn_kwargs
-            )
+                lambda: update(interactive=True),
+                outputs=[self.textbox],
+                api_visibility="undocumented",
+            ).then(**save_fn_kwargs)

         if self.save_history:
             self.new_chat_button.click(

PATCH

echo "Patch applied successfully."
