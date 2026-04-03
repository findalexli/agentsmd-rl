#!/usr/bin/env bash
set -euo pipefail

cd /workspace/selenium

# Idempotent: skip if already applied
if grep -q 'name = "closure-test"' javascript/atoms/BUILD.bazel 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/javascript/atoms/BUILD.bazel b/javascript/atoms/BUILD.bazel
index 5d86e381b1ff5..b6b787107fb39 100644
--- a/javascript/atoms/BUILD.bazel
+++ b/javascript/atoms/BUILD.bazel
@@ -403,7 +403,7 @@ closure_js_deps(
 )

 closure_test_suite(
-    name = "test",
+    name = "closure-test",
     data = [
         ":atoms",
         ":deps",
diff --git a/javascript/atoms/README.md b/javascript/atoms/README.md
index d545c520e53be..9c646a2a5ad08 100644
--- a/javascript/atoms/README.md
+++ b/javascript/atoms/README.md
@@ -14,7 +14,7 @@ the code in your IDE of choice, and then run the tests in a
 browser. You can do this by starting a debug server:

 ```shell
-bazel run javascript/atoms:test_debug_server
+bazel run javascript/atoms:closure-test_debug_server
 ```

 And then navigating to: <http://localhost:2310/filez/_main/javascript/atoms/>
@@ -32,12 +32,12 @@ the `bazel run` command.
 You can run all the tests for a browser using:

 ```shell
-bazel test //javascript/atoms:test{,-chrome,-edge,-safari}
+bazel test //javascript/atoms:closure-test{,-chrome,-edge,-safari}
 ```

 You can also filter to a specific test using the name of the file
 stripped of it's `.html` suffix. For example:

 ```shell
-bazel test --test_filter=shown_test --//common:headless=false javascript/atoms:test-chrome
+bazel test --test_filter=shown_test --//common:headless=false javascript/atoms:closure-test-chrome
 ```
diff --git a/javascript/chrome-driver/BUILD.bazel b/javascript/chrome-driver/BUILD.bazel
index ad4bfe406c496..0b49bdb1123b3 100644
--- a/javascript/chrome-driver/BUILD.bazel
+++ b/javascript/chrome-driver/BUILD.bazel
@@ -165,7 +165,7 @@ closure_js_deps(
 )

 closure_test_suite(
-    name = "test",
+    name = "closure-test",
     data = [
         ":all_files",
         ":deps",
diff --git a/javascript/webdriver/BUILD.bazel b/javascript/webdriver/BUILD.bazel
index f7babc33bc676..cb3422d601fe7 100644
--- a/javascript/webdriver/BUILD.bazel
+++ b/javascript/webdriver/BUILD.bazel
@@ -64,7 +64,7 @@ closure_js_deps(
 )

 closure_test_suite(
-    name = "test",
+    name = "closure-test",
     data = [
         ":all_files",
         ":deps",

PATCH

echo "Patch applied successfully."
