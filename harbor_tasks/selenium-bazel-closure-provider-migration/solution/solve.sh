#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for PR #17317
cat <<'PATCH' | git apply -
diff --git a/javascript/private/header.bzl b/javascript/private/header.bzl
index e54f0296167cd..b0652770832f7 100644
--- a/javascript/private/header.bzl
+++ b/javascript/private/header.bzl
@@ -1,3 +1,5 @@
+load("@rules_closure//closure/private:defs.bzl", "ClosureJsBinaryInfo")
+
 _browser_names = [
     "android",
     "chrome",
@@ -11,12 +13,12 @@ def _closure_lang_file_impl(ctx):
     suffixes = ["_%s" % n for n in _browser_names]

     for d in ctx.attr.deps:
-        if getattr(d, "closure_js_binary", None):
+        if ClosureJsBinaryInfo in d:
             name = d.label.name.replace("-", "_")
             for suffix in suffixes:
                 if name.endswith(suffix):
                     name = name[0:-len(suffix)]
-            binaries.update({name: d.closure_js_binary.bin})
+            binaries.update({name: d[ClosureJsBinaryInfo].bin})

     args = ctx.actions.args()
     args.add(ctx.attr.lang)
PATCH

echo "Patch applied successfully"
