#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pulumi

# Idempotency: if the distinctive line is already present, the patch was applied.
if grep -q '"typescript": ">= 3.8.3 < 7"' sdk/nodejs/package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/changelog/pending/20260324--sdk-nodejs--allow-typescript-6-as-a-peer-dependency.yaml b/changelog/pending/20260324--sdk-nodejs--allow-typescript-6-as-a-peer-dependency.yaml
new file mode 100644
index 000000000000..4b526bd2b7aa
--- /dev/null
+++ b/changelog/pending/20260324--sdk-nodejs--allow-typescript-6-as-a-peer-dependency.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: fix
+  scope: sdk/nodejs
+  description: Allow TypeScript 6 as a peer dependency
diff --git a/sdk/nodejs/Makefile b/sdk/nodejs/Makefile
index 0017a42902da..4d8a10ab0dd6 100644
--- a/sdk/nodejs/Makefile
+++ b/sdk/nodejs/Makefile
@@ -97,15 +97,16 @@ test_integration:: $(TEST_ALL_DEPS)
 	node 'bin/tests/runtime/closure-integration-tests.js'
 	node 'bin/tests/runtime/install-package-tests.js'

-TSC_SUPPORTED_VERSIONS = ~3.8.3 ^3 ^4
+TSC_SUPPORTED_VERSIONS = ~3.8.3 ^3 ^4 ^6

 version=$(subst sxs_test_,,$(word 1,$(subst !, ,$@)))
 sxs_test_%:
 	@cd tests/sxs_ts_test && ( \
 		cp -f package$(version).json package.json && \
+		if [ -f tsconfig$(version).json ]; then project=tsconfig$(version).json; else project=tsconfig.json; fi && \
 		yarn install && \
 		yarn run tsc --version && \
-		yarn run tsc &&  \
+		yarn run tsc --project $$project && \
 		rm package.json && \
 		echo "✅ TypeScript $(version) passed" \
 	) || ( \
diff --git a/sdk/nodejs/biome.json b/sdk/nodejs/biome.json
index 9e12f7338dcd..9e5b997724ef 100644
--- a/sdk/nodejs/biome.json
+++ b/sdk/nodejs/biome.json
@@ -14,6 +14,7 @@
             "cmd/pulumi-language-nodejs",
             "tests/mockpackage/lib/",
             "tests/runtime/testdata/closure-tests",
+            "tests/sxs_ts_test/tsconfig*.json",
             "tools/automation/output/",
             "vendor/"
         ]
diff --git a/sdk/nodejs/package.json b/sdk/nodejs/package.json
index 93269346201a..324666557dbe 100644
--- a/sdk/nodejs/package.json
+++ b/sdk/nodejs/package.json
@@ -65,7 +65,7 @@
     },
     "peerDependencies": {
         "ts-node": ">= 7.0.1 < 12",
-        "typescript": ">= 3.8.3 < 6"
+        "typescript": ">= 3.8.3 < 7"
     },
     "peerDependenciesMeta": {
         "typescript": {
diff --git a/sdk/nodejs/tests/sxs_ts_test/package^6.json b/sdk/nodejs/tests/sxs_ts_test/package^6.json
new file mode 100644
index 000000000000..1e0cdb7ca536
--- /dev/null
+++ b/sdk/nodejs/tests/sxs_ts_test/package^6.json
@@ -0,0 +1,12 @@
+{
+    "name": "sxs",
+    "version": "${VERSION}",
+    "license": "Apache-2.0",
+    "dependencies": {
+        "@pulumi/pulumi": "latest",
+        "typescript": "^6"
+    },
+    "devDependencies": {
+        "@types/node": "^18.0.0"
+    }
+}
diff --git a/sdk/nodejs/tests/sxs_ts_test/tsconfig^6.json b/sdk/nodejs/tests/sxs_ts_test/tsconfig^6.json
new file mode 100644
index 000000000000..40bdb0f54afb
--- /dev/null
+++ b/sdk/nodejs/tests/sxs_ts_test/tsconfig^6.json
@@ -0,0 +1,9 @@
+{
+    "extends": "./tsconfig.json",
+    "compilerOptions": {
+        // TS6 deprecated moduleResolution: "node". Override to "nodenext" which behaves
+        // identically for CJS projects (no "type": "module" in package.json).
+        "module": "nodenext",
+        "moduleResolution": "nodenext"
+    }
+}
PATCH

echo "Gold patch applied."
