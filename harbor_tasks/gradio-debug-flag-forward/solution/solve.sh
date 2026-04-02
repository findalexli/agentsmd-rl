#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if create_app already accepts debug parameter, skip
if grep -q 'debug: bool = False' gradio/routes.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/blocks.py b/gradio/blocks.py
index 234869cff0..d23cb2b8fc 100644
--- a/gradio/blocks.py
+++ b/gradio/blocks.py
@@ -2716,6 +2716,7 @@ def reverse(text):
             strict_cors=strict_cors,
             ssr_mode=self.ssr_mode,
             mcp_server=mcp_server,
+            debug=debug,
         )
         if self.mcp_error and not quiet:
             print(self.mcp_error)
diff --git a/gradio/routes.py b/gradio/routes.py
index 6488f395d6..e9c5a7ee78 100644
--- a/gradio/routes.py
+++ b/gradio/routes.py
@@ -435,6 +435,7 @@ def create_app(
         strict_cors: bool = True,
         ssr_mode: bool = False,
         mcp_server: bool | None = None,
+        debug: bool = False,
     ) -> App:
         app_kwargs = app_kwargs or {}
         app_kwargs.setdefault("default_response_class", ORJSONResponse)
@@ -444,7 +445,7 @@ def create_app(
         app_kwargs["lifespan"] = create_lifespan_handler(
             app_kwargs.get("lifespan", None), *delete_cache
         )
-        app = App(auth_dependency=auth_dependency, **app_kwargs, debug=True)
+        app = App(auth_dependency=auth_dependency, **app_kwargs, debug=debug)
         if blocks.mcp_server_obj:
             blocks.mcp_server_obj.launch_mcp_on_sse(app, mcp_subpath, blocks.root_path)
         router = APIRouter(prefix=API_PREFIX)

PATCH

echo "Patch applied successfully."
