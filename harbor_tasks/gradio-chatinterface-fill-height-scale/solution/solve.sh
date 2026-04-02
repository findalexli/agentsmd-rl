#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency: check if fill_height scale propagation is already present in init.svelte.ts
if grep -q 'fill_height.*?.*1.*:.*null' js/core/src/init.svelte.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/chat_interface.py b/gradio/chat_interface.py
index 1fddc35262..529b6a0626 100644
--- a/gradio/chat_interface.py
+++ b/gradio/chat_interface.py
@@ -329,10 +329,10 @@ def _render_chatbot_area(
             )
             self.chatbot._setup_examples()
         else:
+            # Use default height of chatbot
             self.chatbot = Chatbot(
                 label=I18nData("chat_interface.chatbot"),
                 scale=1,
-                height=400 if self.fill_height else None,
                 autoscroll=self.autoscroll,
                 examples=(
                     self.examples_messages
diff --git a/js/core/src/Blocks.svelte b/js/core/src/Blocks.svelte
index 3efab27035..ff386030d0 100644
--- a/js/core/src/Blocks.svelte
+++ b/js/core/src/Blocks.svelte
@@ -171,7 +171,8 @@
 			version,
 			api_prefix,
 			max_file_size,
-			autoscroll
+			autoscroll,
+			fill_height
 		},
 		app,
 		$reactive_formatter,
@@ -256,7 +257,8 @@
 				version,
 				api_prefix,
 				max_file_size,
-				autoscroll
+				autoscroll,
+				fill_height
 			});
 			dep_manager.reload(
 				dependencies,
diff --git a/js/core/src/init.svelte.ts b/js/core/src/init.svelte.ts
index d7fb4e8e00..b7937b96c2 100644
--- a/js/core/src/init.svelte.ts
+++ b/js/core/src/init.svelte.ts
@@ -325,7 +325,8 @@ export class AppTree {
 				props: {
 					visible: true,
 					root: "",
-					theme_mode: "light"
+					theme_mode: "light",
+					scale: this.#config.fill_height ? 1 : null
 				},
 				component_class_id: "column",
 				key: null
diff --git a/js/core/src/types.ts b/js/core/src/types.ts
index dd5b5437e9..d0ff54b331 100644
--- a/js/core/src/types.ts
+++ b/js/core/src/types.ts
@@ -128,4 +128,5 @@ export interface AppConfig {
 	autoscroll: boolean;
 	api_prefix: string;
 	api_url: string;
+	fill_height?: boolean;
 }

PATCH

echo "Patch applied successfully."
