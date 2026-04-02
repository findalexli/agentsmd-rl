#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied (distinctive line from the fix)
if grep -q 'interface_fn = kwargs.pop("fn"' gradio/external.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/external.py b/gradio/external.py
index 66e1a9de93..0496c5b636 100644
--- a/gradio/external.py
+++ b/gradio/external.py
@@ -501,11 +501,13 @@ def query_huggingface_inference_endpoints(*data):

     kwargs = dict(interface_info, **kwargs)

-    fn = kwargs.pop("fn", None)
+    interface_fn = kwargs.pop("fn", None)
     inputs = kwargs.pop("inputs", None)
     outputs = kwargs.pop("outputs", None)

-    interface = gr.Interface(fn, inputs, outputs, **kwargs, api_name="predict")
+    interface = gr.Interface(
+        interface_fn, inputs, outputs, **kwargs, api_name="predict"
+    )
     return interface


diff --git a/gradio/external_utils.py b/gradio/external_utils.py
index 4f31c651df..15bcb3e0cb 100644
--- a/gradio/external_utils.py
+++ b/gradio/external_utils.py
@@ -326,8 +326,13 @@ def handle_hf_error(e: Exception):
         raise TooManyRequestsError() from e
     elif "401" in str(e) or "You must provide an api_key" in str(e):
         raise Error("Unauthorized, please make sure you are signed in.") from e
+    elif isinstance(e, StopIteration):
+        raise Error(
+            "This model is not supported by any Hugging Face Inference Provider. "
+            "Please check the supported models at https://huggingface.co/docs/inference-providers."
+        ) from e
     else:
-        raise Error(str(e)) from e
+        raise Error(str(e) or f"An error occurred: {type(e).__name__}") from e


 def create_endpoint_fn(

PATCH

echo "Patch applied successfully."
