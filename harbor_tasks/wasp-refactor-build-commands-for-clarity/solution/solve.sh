#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wasp

# Idempotent: skip if already applied
if grep -q 'build:hs)' waspc/run 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/workflows/ci-waspc-build.yaml b/.github/workflows/ci-waspc-build.yaml
index de6795baab..c9be26bbf0 100644
--- a/.github/workflows/ci-waspc-build.yaml
+++ b/.github/workflows/ci-waspc-build.yaml
@@ -122,8 +122,9 @@ jobs:
         working-directory: waspc
         env:
           LC_ALL: C.UTF-8 # In some Docker containers the LOCALE is not UTF-8 by default
+          BUILD_STATIC: ${{ matrix.env.static && '1' || '' }}
         run: |
-          ./run build:all${{ matrix.env.static && ':static' || '' }}
+          ./run build
           mkdir -p artifacts
           ./tools/make_binary_package.sh "artifacts/${{ steps.compute-artifact-names.outputs.tarball-name }}"

diff --git a/waspc/README.md b/waspc/README.md
index c4cacce065..21e0c7b1d4 100644
--- a/waspc/README.md
+++ b/waspc/README.md
@@ -73,7 +73,7 @@ Check [.nvmrc](.nvmrc) file to learn which version of `node` that should be.
 ### Build

 ```sh
-./run build:all
+./run build
 ```

 to build the whole `waspc` project.
@@ -102,7 +102,7 @@ to ensure all the tests are passing.
 ./run wasp-cli
 ```

-to run the `wasp-cli` executable (that you previously built with `./run build:all`)!
+to run the `wasp-cli` executable (that you previously built with `./run build`)!

 Since you provided no arguments, you should see help/usage.

@@ -158,7 +158,7 @@ When done, new tab in your browser should open and you will see the Kitchen Sink
 3. Do a change in the codebase (most often in `src/` or `cli/src/` or `data/`), and update tests if that makes sense (see [Test](#tests)).
    Fix any errors shown by HLS/`ghcid`.
    Rinse and repeat. If you're an internal team member, postpone updating waspc e2e tests tests until approval (see [here](#note-for-team-members)).
-4. Use `./run build` to build the Haskell/cabal project, and `./run wasp-cli` to both build and run it. If you changed code in `data/packages/`, you will also need to run `./run build:packages` (check [TypeScript Packages section](#typescript-packages) for more details). Alternatively, you can also run slower `./run build:all` to at the same time build Haskell, TS packages, and any other piece of the project in one command.
+4. Use `./run build:hs` to build the Haskell/cabal project, and `./run wasp-cli` to both build and run it. If you changed code in `data/packages/`, you will also need to run `./run build:packages` (check [TypeScript Packages section](#typescript-packages) for more details). Alternatively, you can also run slower `./run build` to at the same time build Haskell, TS packages, and any other piece of the project in one command.
 5. For easier manual testing of the changes you did on a Wasp app, you have the [`kitchen-sink`](../examples/kitchen-sink/) app, which we always keep updated. Also, if you added a new feature, add it to this app (+ tests) if needed. Check its README for more details (including how to run it).
 6. Run `./run test` to confirm that all the tests are passing. If needed, accept changes in the waspc e2e tests with `./run test:waspc:e2e:accept-all`. Check "Tests" for more info.
 7. If you did a bug fix, added new feature or did a breaking change, add short info about it to `Changelog.md`. Also, bump version in `waspc.cabal` and `ChangeLog.md` if needed. If you are not sure how to decide which version to go with, check out [how we determine the next version](#determining-next-version).
diff --git a/waspc/run b/waspc/run
index 2d009a2989..d910cd5825 100755
--- a/waspc/run
+++ b/waspc/run
@@ -22,10 +22,9 @@ DEFAULT_COLOR="\033[39m"
 WASP_PACKAGES_COMPILE="for pkg in ${SCRIPT_DIR}/data/packages/*/package.json; do \
   (cd \$(dirname \$pkg) && npm install && npm run build); \
 done"
-BUILD_HS_CMD="cabal build all"
+BUILD_HS_CMD="cabal build all ${BUILD_STATIC:+--enable-executable-static}"
 BUILD_HS_FULL_CMD="cabal build all --enable-tests --enable-benchmarks"
 BUILD_ALL_CMD="$WASP_PACKAGES_COMPILE && $BUILD_HS_CMD"
-BUILD_ALL_STATIC_CMD="$WASP_PACKAGES_COMPILE && $BUILD_HS_CMD --enable-executable-static"

 INSTALL_CMD="$WASP_PACKAGES_COMPILE && cabal install --overwrite-policy=always"

@@ -118,14 +117,11 @@ print_usage() {
   echo_bold "COMMANDS"

   print_usage_cmd "build" \
-    "Builds the Haskell project."
-  print_usage_cmd "build:all" \
-    "Builds the Haskell project + all sub-projects (i.e. TS packages)."
-  print_usage_cmd "build:all:static" \
-    "Builds the Haskell project statically + all sub-projects (i.e. TS packages). Only useful for release builds. Needs to be run on a musl-based Linux distribution (e.g. Alpine)."
+    "Builds the Haskell project + all sub-projects (i.e. TS packages). Run with the \`BUILD_STATIC=1\` env to build statically."
+  print_usage_cmd "build:hs" \
+    "Builds the Haskell project only. Run with the \`BUILD_STATIC=1\` env to build statically."
   print_usage_cmd "build:packages" \
     "Builds the TypeScript projects under data/packages/."
-  echo ""
   print_usage_cmd "wasp-cli <args>" \
     "Runs the dev version of wasp executable while forwarding arguments. Builds the project (hs) first if needed. Doesn't require you to be in the waspc project to run it."
   echo ""
@@ -189,13 +185,10 @@ exitStatusToString() {

 case $COMMAND in
   build)
-    echo_and_eval "$BUILD_HS_CMD"
-    ;;
-  build:all)
     echo_and_eval "$BUILD_ALL_CMD"
     ;;
-  build:all:static)
-    echo_and_eval "$BUILD_ALL_STATIC_CMD"
+  build:hs)
+    echo_and_eval "$BUILD_HS_CMD"
     ;;
   build:packages)
     echo_and_eval "$WASP_PACKAGES_COMPILE"
diff --git a/waspc/run.ps1 b/waspc/run.ps1
index eaa8612b3f..0210be6ce5 100644
--- a/waspc/run.ps1
+++ b/waspc/run.ps1
@@ -17,11 +17,11 @@ $RUN_CMD="cabal --project-dir=${PROJECT_ROOT} run wasp-cli -- $Args"

 switch ($Command) {
     "build" {
-        Invoke-Expression $BUILD_HS_CMD
-    }
-    "build:all" {
         Invoke-Expression $BUILD_ALL_CMD
     }
+    "build:hs" {
+        Invoke-Expression $BUILD_HS_CMD
+    }
     "build:packages" {
         Invoke-Expression $WASP_PACKAGES_COMPILE
     }
@@ -33,8 +33,9 @@ switch ($Command) {
         Write-Host "  run <command>"
         Write-Host ""
         Write-Host "COMMANDS"
-        Write-Host "  build             Builds the Haskell project."
-        Write-Host "  build:all         Builds the Haskell project + all sub-projects (i.e. TS packages)."
+        Write-Host "  build             Builds the Haskell project + all sub-projects (i.e. TS packages)."
+        Write-Host "  build:hs          Builds the Haskell project only."
+        Write-Host "  build:packages    Builds the TypeScript projects under data/packages/."
         Write-Host "  wasp-cli <args>   Runs the dev version of wasp executable while forwarding arguments."
         Write-Host "                    Builds the project (hs) first if needed. Doesn't require you to be in the waspc project to run it."
     }

PATCH

echo "Patch applied successfully."
