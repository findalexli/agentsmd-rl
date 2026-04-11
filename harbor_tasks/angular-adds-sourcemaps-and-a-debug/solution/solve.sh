#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

# Idempotent: skip if already applied
if grep -q 'def esbuild(minify' devtools/tools/defaults.bzl 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/devtools/BUILD.bazel b/devtools/BUILD.bazel
index 207b4561c183..564c13c3dd7b 100644
--- a/devtools/BUILD.bazel
+++ b/devtools/BUILD.bazel
@@ -1,7 +1,20 @@
+load("@bazel_skylib//rules:common_settings.bzl", "bool_flag")
 load("//devtools/tools:defaults.bzl", "ts_config")

 package(default_visibility = ["//visibility:public"])

+bool_flag(
+    name = "debug",
+    build_setting_default = False,
+)
+
+config_setting(
+    name = "debug_build",
+    flag_values = {
+        ":debug": "True",
+    },
+)
+
 exports_files([
     "tsconfig.json",
     "cypress.json",
diff --git a/devtools/README.md b/devtools/README.md
index 29b6ca172e30..c918ec226c16 100644
--- a/devtools/README.md
+++ b/devtools/README.md
@@ -50,6 +50,40 @@ This would start a development server that you can access on <http://localhost:4
 uses a "development shell." This is different from "chrome shell" in a way, that it runs the user's app in an iframe.
 DevTools then communicate with the user's app via message passing.

+#### Dev Install
+
+To actually build and install as a real browser extension in dev mode, use:
+
+```shell
+pnpm devtools:build:chrome:debug
+```
+
+This will build the extension at `dist/bin/devtools/projects/shell-browser/src/prodapp`. Then go to `chrome://extensions`,
+enable developer mode, and click "Load unpacked" to load the extension from that directory.
+
+Whenever you rebuild the extension, make sure to reload the extension in `chrome://extensions`, right click on the
+Angular DevTools panel and click "Reload frame", and refresh the page you're inspecting to make sure changes are applied.
+
+#### Debugging
+
+Depending on which script you want to debug, you can find them in different locations. In debug mode, these should all
+have sourcemaps loaded and be unminified.
+
+- The main "Angular DevTools" panel UI runs in its own frame and can be found by clicking "Inspect Element" directly
+  on that UI.
+  - Note that this inspects _all_ of Chrome DevTools, which loads Angular DevTools in an iframe.
+  - The right entry point is under `index.html/ienfalfjdbdpebioblfackkekamfmbnh/...`
+- Scripts directly executed in the inspected page content's can be found in the normal Sources panel under "Angular DevTools".
+  - `backend_bundle.js`
+  - `detect_angular_bundle.js`
+- Content scripts are executed in the inspected page, but within an isolated environment and found in the normal Sources panel,
+  but under the "Content Scripts" section (as opposed to "Page", "Workspace", "Overrides", etc., you may need to click an
+  arrow to expand the list of sections).
+  - `content_script_bundle.js`
+  - `ng_validate_bundle.js`
+- The background service worker is found at `chrome://extensions`.
+  - Click on the "Angular DevTools" extension and the "Inspect Views > service worker" button to open a debugger.
+
 ### Running End-to-End Tests

 Before running end-to-end tests, you need to start the development server using:
diff --git a/devtools/projects/shell-browser/src/BUILD.bazel b/devtools/projects/shell-browser/src/BUILD.bazel
index a758cb22870b..77c5cc21f5fc 100644
--- a/devtools/projects/shell-browser/src/BUILD.bazel
+++ b/devtools/projects/shell-browser/src/BUILD.bazel
@@ -42,7 +42,6 @@ esbuild(
     ],
     config = "//devtools/tools/esbuild:esbuild-esm-prod.config.mjs",
     entry_points = [":main.ts"],
-    minify = True,
     platform = "browser",
     splitting = False,
     target = "es2022",
@@ -62,7 +61,6 @@ esbuild(
     config = "//devtools/tools/esbuild:esbuild-esm.config.mjs",
     entry_point = "devtools.ts",
     format = "iife",
-    minify = True,
     platform = "browser",
     splitting = False,
     target = "es2022",
diff --git a/devtools/projects/shell-browser/src/app/BUILD.bazel b/devtools/projects/shell-browser/src/app/BUILD.bazel
index 4cbb6d3c855a..ce8da3d9bba5 100644
--- a/devtools/projects/shell-browser/src/app/BUILD.bazel
+++ b/devtools/projects/shell-browser/src/app/BUILD.bazel
@@ -213,8 +213,9 @@ esbuild(
     config = "//devtools/tools/esbuild:esbuild-iife.config.mjs",
     entry_point = "detect-angular.ts",
     format = "iife",
-    minify = True,
     platform = "browser",
+    # Need to inline sourcemaps for injected scripts as Chrome doesn't seem to load them correctly otherwise.
+    sourcemap = "inline",
     splitting = False,
     target = "esnext",
     deps = [
@@ -232,8 +233,9 @@ esbuild(
     config = "//devtools/tools/esbuild:esbuild-iife.config.mjs",
     entry_point = "backend.ts",
     format = "iife",
-    minify = True,
     platform = "browser",
+    # Need to inline sourcemaps for injected scripts as Chrome doesn't seem to load them correctly otherwise.
+    sourcemap = "inline",
     splitting = False,
     target = "esnext",
     deps = [
@@ -251,8 +253,9 @@ esbuild(
     config = "//devtools/tools/esbuild:esbuild-iife.config.mjs",
     entry_point = "ng-validate.ts",
     format = "iife",
-    minify = True,
     platform = "browser",
+    # Need to inline sourcemaps for injected scripts as Chrome doesn't seem to load them correctly otherwise.
+    sourcemap = "inline",
     splitting = False,
     target = "esnext",
     deps = [
@@ -270,7 +273,6 @@ esbuild(
     config = "//devtools/tools/esbuild:esbuild-iife.config.mjs",
     entry_point = "background.ts",
     format = "iife",
-    minify = True,
     platform = "browser",
     splitting = False,
     target = "esnext",
@@ -289,8 +291,9 @@ esbuild(
     config = "//devtools/tools/esbuild:esbuild-iife.config.mjs",
     entry_point = "content-script.ts",
     format = "iife",
-    minify = True,
     platform = "browser",
+    # Need to inline sourcemaps for injected scripts as Chrome doesn't seem to load them correctly otherwise.
+    sourcemap = "inline",
     splitting = False,
     target = "esnext",
     deps = [
diff --git a/devtools/tools/defaults.bzl b/devtools/tools/defaults.bzl
index b2f610bf792c..5f96520bb91d 100644
--- a/devtools/tools/defaults.bzl
+++ b/devtools/tools/defaults.bzl
@@ -23,7 +23,18 @@ sass_library = _sass_library
 npm_sass_library = _npm_sass_library
 http_server = _http_server
 js_library = _js_library
-esbuild = _esbuild
+
+def esbuild(minify = None, sourcemap = "linked", sources_content = True, **kwargs):
+    _esbuild(
+        minify = minify if minify != None else select({
+            "//devtools:debug_build": False,
+            "//conditions:default": True,
+        }),
+        sourcemap = sourcemap,
+        sources_content = sources_content,
+        **kwargs
+    )
+
 copy_to_bin = _copy_to_bin
 copy_to_directory = _copy_to_directory
 string_flag = _string_flag
diff --git a/package.json b/package.json
index 45ad69eb820b..408a9ba3698a 100644
--- a/package.json
+++ b/package.json
@@ -37,7 +37,9 @@
     "devtools:e2e:open": "cypress open --project ./devtools/cypress",
     "devtools:build:chrome": "bazelisk build --//devtools/projects/shell-browser/src:flag_browser=chrome //devtools/projects/shell-browser/src:prodapp",
     "devtools:build:firefox": "bazelisk build --config snapshot-build-firefox --//devtools/projects/shell-browser/src:flag_browser=firefox //devtools/projects/shell-browser/src:prodapp",
+    "devtools:build:chrome:debug": "pnpm run -s devtools:build:chrome --//devtools:debug",
     "devtools:build:chrome:release": "pnpm run -s devtools:build:chrome",
+    "devtools:build:firefox:debug": "pnpm run -s devtools:build:firefox --//devtools:debug",
     "devtools:build:firefox:release": "pnpm run -s devtools:build:firefox --jobs 4",
     "devtools:test": "bazelisk test --//devtools/projects/shell-browser/src:flag_browser=chrome -- //devtools/...",
     "devtools:test:unit": "bazelisk test -- //devtools/...",

PATCH

echo "Patch applied successfully."
