#!/usr/bin/env bash
set -euo pipefail

cd /workspace/selenium

# Idempotent: skip if already applied
if grep -q 'build_setting_default = True' common/BUILD.bazel 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.bazelrc.remote b/.bazelrc.remote
index a858484cb1976..3aaff34596a2b 100644
--- a/.bazelrc.remote
+++ b/.bazelrc.remote
@@ -42,9 +42,6 @@ test:rbe --test_env=HOME=/home/dev
 # Make sure we sniff credentials properly
 build:rbe --credential_helper=gypsum.cluster.engflow.com=%workspace%/scripts/credential-helper.sh

-# Use pinned browsers when running remotely
-build:rbe --//common:pin_browsers
-
 # The remote build machines are pretty small, and 50 threads may leave them
 # thrashing, but our dev machines are a lot larger. Scale the workload so we
 # make reasonable usage of everything, everywhere, all at once.
diff --git a/.github/workflows/ci-dotnet.yml b/.github/workflows/ci-dotnet.yml
index 1e2a2c259382d..0c88afd629d4c 100644
--- a/.github/workflows/ci-dotnet.yml
+++ b/.github/workflows/ci-dotnet.yml
@@ -24,4 +24,4 @@ jobs:
       os: windows
       run: |
         fsutil 8dot3name set 0
-        bazel test //dotnet/test/common:ElementFindingTest-firefox //dotnet/test/common:ElementFindingTest-chrome --pin_browsers=true
+        bazel test //dotnet/test/common:ElementFindingTest-firefox //dotnet/test/common:ElementFindingTest-chrome
diff --git a/.github/workflows/ci-java.yml b/.github/workflows/ci-java.yml
index 63727764a0953..f04334fba068c 100644
--- a/.github/workflows/ci-java.yml
+++ b/.github/workflows/ci-java.yml
@@ -23,7 +23,7 @@ jobs:
       java-version: 17
       run: |
         fsutil 8dot3name set 0
-        bazel test --flaky_test_attempts 3 --pin_browsers=true //java/test/org/openqa/selenium/chrome:ChromeDriverFunctionalTest `
+        bazel test --flaky_test_attempts 3 //java/test/org/openqa/selenium/chrome:ChromeDriverFunctionalTest `
             //java/test/org/openqa/selenium/federatedcredentialmanagement:FederatedCredentialManagementTest `
             //java/test/org/openqa/selenium/firefox:FirefoxDriverBuilderTest `
             //java/test/org/openqa/selenium/grid/router:RemoteWebDriverDownloadTest `
@@ -48,7 +48,7 @@ jobs:
       # https://github.com/bazelbuild/rules_jvm_external/issues/1046
       java-version: 17
       run: |
-        bazel test --flaky_test_attempts 3 --pin_browsers=true //java/test/org/openqa/selenium/chrome:ChromeDriverFunctionalTest-remote \
+        bazel test --flaky_test_attempts 3 //java/test/org/openqa/selenium/chrome:ChromeDriverFunctionalTest-remote \
             //java/test/org/openqa/selenium/federatedcredentialmanagement:FederatedCredentialManagementTest \
           //java/test/org/openqa/selenium/firefox:FirefoxDriverBuilderTest \
             //java/test/org/openqa/selenium/grid/router:RemoteWebDriverDownloadTest \
@@ -72,4 +72,4 @@ jobs:
       # https://github.com/bazelbuild/rules_jvm_external/issues/1046
       java-version: 17
       run: |
-        bazel test --flaky_test_attempts 3 --pin_browsers=true //java/test/org/openqa/selenium/chrome:ChromeDriverFunctionalTest-remote
+        bazel test --flaky_test_attempts 3 //java/test/org/openqa/selenium/chrome:ChromeDriverFunctionalTest-remote
diff --git a/.github/workflows/ci-python.yml b/.github/workflows/ci-python.yml
index 6750bd1b73a11..4136353d96d6a 100644
--- a/.github/workflows/ci-python.yml
+++ b/.github/workflows/ci-python.yml
@@ -114,7 +114,7 @@ jobs:
       os: ${{ matrix.os }}
       cache-key: py-browser-${{ matrix.browser }}
       run: |
-        bazel test --local_test_jobs 1 --flaky_test_attempts 3 --pin_browsers=true //py:common-${{ matrix.browser }}-bidi //py:test-${{ matrix.browser }}
+        bazel test --local_test_jobs 1 --flaky_test_attempts 3 //py:common-${{ matrix.browser }}-bidi //py:test-${{ matrix.browser }}

   browser-tests-windows:
     name: Browser Tests
@@ -135,7 +135,7 @@ jobs:
       cache-key: py-browser-${{ matrix.browser }}
       run: |
         fsutil 8dot3name set 0
-        bazel test --local_test_jobs 1 --flaky_test_attempts 3 --pin_browsers=true //py:common-${{ matrix.browser }}-bidi //py:test-${{ matrix.browser }}
+        bazel test --local_test_jobs 1 --flaky_test_attempts 3 //py:common-${{ matrix.browser }}-bidi //py:test-${{ matrix.browser }}

   browser-tests-macos:
     name: Browser Tests
@@ -153,4 +153,4 @@ jobs:
       os: ${{ matrix.os }}
       cache-key: py-browser-${{ matrix.browser }}
       run: |
-        bazel test --local_test_jobs 1 --flaky_test_attempts 3 --pin_browsers=true //py:common-${{ matrix.browser }} //py:test-${{ matrix.browser }}
+        bazel test --local_test_jobs 1 --flaky_test_attempts 3 //py:common-${{ matrix.browser }} //py:test-${{ matrix.browser }}
diff --git a/.github/workflows/ci-ruby.yml b/.github/workflows/ci-ruby.yml
index 08cff26a7eda3..66e0364ce17ed 100644
--- a/.github/workflows/ci-ruby.yml
+++ b/.github/workflows/ci-ruby.yml
@@ -84,7 +84,6 @@ jobs:
         --local_test_jobs 1
         --test_size_filters large
         --test_tag_filters ${{ matrix.browser }}
-        --pin_browsers
         //rb/spec/...

   integration-tests-remote:
@@ -111,5 +110,4 @@ jobs:
         --local_test_jobs 1
         --test_size_filters large
         --test_tag_filters ${{ matrix.browser }}-remote
-        --pin_browsers
         //rb/spec/...
diff --git a/README.md b/README.md
index e37561e17ee7e..c630b7fd79ff4 100644
--- a/README.md
+++ b/README.md
@@ -297,7 +297,7 @@ There are a number of bazel configurations specific for testing.
 ### Common Options Examples

 Here are examples of arguments we make use of in testing the Selenium code:
-* `--pin_browsers` - run specific browser versions defined in the build (versions are updated regularly)
+* `--pin_browsers=false` - use Selenium Manager to locate browsers/drivers
 * `--headless` - run browsers in headless mode (supported be Chrome, Edge and Firefox)
 * `--flaky_test_attempts 3` - re-run failed tests up to 3 times
 * `--local_test_jobs 1` - control parallelism of tests
@@ -491,19 +491,19 @@ echo '<X.Y.Z>' > rb/.ruby-version
 Run all tests with:

 ```shell
-bazel test //dotnet/test/common:AllTests --pin_browsers=true
+bazel test //dotnet/test/common:AllTests
 ```

 You can run specific tests by specifying the class name:

 ```shell
-bazel test //dotnet/test/common:ElementFindingTest --pin_browsers=true
+bazel test //dotnet/test/common:ElementFindingTest
 ```

 If the module supports multiple browsers:

 ```shell
-bazel test //dotnet/test/common:ElementFindingTest-edge --pin_browsers=true
+bazel test //dotnet/test/common:ElementFindingTest-edge
 ```
diff --git a/common/BUILD.bazel b/common/BUILD.bazel
index d83a1899fb612..f267704b2dd06 100644
--- a/common/BUILD.bazel
+++ b/common/BUILD.bazel
@@ -4,7 +4,7 @@ package(default_visibility = ["//visibility:public"])

 bool_flag(
     name = "pin_browsers",
-    build_setting_default = False,
+    build_setting_default = True,
 )

 config_setting(

PATCH

echo "Patch applied successfully."
