#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wasp

# Idempotent: skip if already applied
if grep -q 'format:ormolu' waspc/run 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/workflows/ci-formatting.yaml b/.github/workflows/ci-formatting.yaml
index 822e009d9c..d6aec7a281 100644
--- a/.github/workflows/ci-formatting.yaml
+++ b/.github/workflows/ci-formatting.yaml
@@ -23,7 +23,7 @@ jobs:
       - name: Run Prettier
         run: |
           npm ci
-          npm run prettier:check
+          npm run check:prettier

   ormolu:
     runs-on: ubuntu-latest
diff --git a/package.json b/package.json
index 6c893e8c20..94f9a76d6a 100644
--- a/package.json
+++ b/package.json
@@ -1,8 +1,8 @@
 {
   "name": "wasp-repo",
   "scripts": {
-    "prettier:check": "prettier --ignore-unknown --check --config .prettierrc .",
-    "prettier:format": "prettier --ignore-unknown --write --config .prettierrc ."
+    "check:prettier": "prettier --ignore-unknown --check --config .prettierrc .",
+    "format:prettier": "prettier --ignore-unknown --write --config .prettierrc ."
   },
   "devDependencies": {
     "prettier": "3.5.3",
diff --git a/waspc/README.md b/waspc/README.md
index 6623cb0e7e..3dde82d7dc 100644
--- a/waspc/README.md
+++ b/waspc/README.md
@@ -331,13 +331,13 @@ Normally we set it up in our editors to run on file save.
 You can also run it manually with

 ```sh
-./run ormolu:check
+./run check:ormolu
 ```

 to see if there is any formatting that needs to be fixed, or with

 ```sh
-./run ormolu:format
+./run format:ormolu
 ```

 to have Ormolu actually format (in-place) all files that need formatting.
diff --git a/waspc/run b/waspc/run
index 046628aaa1..a051f669fe 100755
--- a/waspc/run
+++ b/waspc/run
@@ -98,8 +98,8 @@ function dev_tool_path() {
 STAN_CMD="$BUILD_HS_FULL_CMD && $(install_dev_tool stan) && $(dev_tool_path stan) report ${ARGS[@]}"
 HLINT_CMD="$(install_dev_tool hlint) && $(dev_tool_path hlint) . ${ARGS[@]}"
 PRUNE_JUICE_CMD="$(install_dev_tool prune-juice) && $(dev_tool_path prune-juice) ${ARGS[@]}"
-PRETTIER_CHECK_CMD="(cd .. && npm ci && npm run prettier:check)"
-PRETTIER_FORMAT_CMD="(cd .. && npm ci && npm run prettier:format)"
+PRETTIER_CHECK_CMD="(cd .. && npm ci && npm run check:prettier)"
+PRETTIER_FORMAT_CMD="(cd .. && npm ci && npm run format:prettier)"
 ORMOLU_BASE_CMD="$(install_dev_tool ormolu) && $(dev_tool_path ormolu) --color always --check-idempotence"
 ORMOLU_CHECK_CMD="$ORMOLU_BASE_CMD --mode check "'$'"(git ls-files '*.hs' '*.hs-boot')"
 ORMOLU_FORMAT_CMD="$ORMOLU_BASE_CMD --mode inplace "'$'"(git ls-files '*.hs' '*.hs-boot')"
@@ -189,18 +189,22 @@ print_usage() {
     "Runs linter on the codebase."
   print_usage_cmd "prune-juice <args>" \
     "Runs prune-juice on the codebase, which detects unused dependencies."
-  print_usage_cmd "ormolu:check" \
-    "Runs the Haskell code formatter and reports if code is correctly formatted or not."
-  print_usage_cmd "ormolu:format" \
+  print_usage_cmd "format" \
+    "Runs all code formatters (ormolu, cabal-gild, prettier) and formats the code in place."
+  print_usage_cmd "check" \
+    "Runs all code formatters in check mode and reports if code is correctly formatted or not."
+  print_usage_cmd "format:ormolu" \
     "Runs the Haskell code formatter and formats the code in place."
-  print_usage_cmd "cabal-gild:check" \
-    "Runs the .cabal file formatter and reports if code is correctly formatted or not."
-  print_usage_cmd "cabal-gild:format" \
+  print_usage_cmd "check:ormolu" \
+    "Runs the Haskell code formatter and reports if code is correctly formatted or not."
+  print_usage_cmd "format:cabal" \
     "Runs the .cabal file formatter and formats the code in place."
-  print_usage_cmd "prettier:check" \
-    "Runs the repo-wide code formatter and reports if code is correctly formatted or not."
-  print_usage_cmd "prettier:format" \
+  print_usage_cmd "check:cabal" \
+    "Runs the .cabal file formatter and reports if code is correctly formatted or not."
+  print_usage_cmd "format:prettier" \
     "Runs the repo-wide code formatter and formats the code in place."
+  print_usage_cmd "check:prettier" \
+    "Runs the repo-wide code formatter and reports if code is correctly formatted or not."
   print_usage_cmd "module-graph" \
     "Creates graph of modules in the project. Needs graphmod (available on hackage) and graphviz (your os distribution) installed."
   echo ""
@@ -298,24 +302,34 @@ case $COMMAND in
   prune-juice)
     echo_and_eval "$PRUNE_JUICE_CMD"
     ;;
-  ormolu:check)
+  format)
+    echo_and_eval "$ORMOLU_FORMAT_CMD"
+    echo_and_eval "$CABAL_GILD_FORMAT_CMD"
+    echo_and_eval "$PRETTIER_FORMAT_CMD"
+    ;;
+  check)
     echo_and_eval "$ORMOLU_CHECK_CMD"
+    echo_and_eval "$CABAL_GILD_CHECK_CMD"
+    echo_and_eval "$PRETTIER_CHECK_CMD"
     ;;
-  ormolu:format)
+  format:ormolu)
     echo_and_eval "$ORMOLU_FORMAT_CMD"
     ;;
-  cabal-gild:check)
-    echo_and_eval "$CABAL_GILD_CHECK_CMD"
+  check:ormolu)
+    echo_and_eval "$ORMOLU_CHECK_CMD"
     ;;
-  cabal-gild:format)
+  format:cabal)
     echo_and_eval "$CABAL_GILD_FORMAT_CMD"
     ;;
-  prettier:check)
-    echo_and_eval "$PRETTIER_CHECK_CMD"
+  check:cabal)
+    echo_and_eval "$CABAL_GILD_CHECK_CMD"
     ;;
-  prettier:format)
+  format:prettier)
     echo_and_eval "$PRETTIER_FORMAT_CMD"
     ;;
+  check:prettier)
+    echo_and_eval "$PRETTIER_CHECK_CMD"
+    ;;
   code-check)
     echo_and_eval "$PRETTIER_CHECK_CMD"
     PRETTIER_RESULT=$?

PATCH

echo "Patch applied successfully."
