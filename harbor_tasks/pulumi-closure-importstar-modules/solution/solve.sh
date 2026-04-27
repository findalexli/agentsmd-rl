#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pulumi

# Idempotency: if patch already applied, skip
if grep -q "isImportStarResult" sdk/nodejs/runtime/closure/createClosure.ts 2>/dev/null; then
    echo "Gold patch already applied; skipping."
else
    git apply --whitespace=nowarn <<'PATCH'
diff --git a/changelog/pending/20260330--sdk-nodejs--fix-closure-serialization-for-__importstar-wrapped-modules.yaml b/changelog/pending/20260330--sdk-nodejs--fix-closure-serialization-for-__importstar-wrapped-modules.yaml
new file mode 100644
index 000000000000..0186d6ae4843
--- /dev/null
+++ b/changelog/pending/20260330--sdk-nodejs--fix-closure-serialization-for-__importstar-wrapped-modules.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: fix
+  scope: sdk/nodejs
+  description: Fix closure serialization for __importStar-wrapped modules
diff --git a/sdk/nodejs/runtime/closure/createClosure.ts b/sdk/nodejs/runtime/closure/createClosure.ts
index 14107cfd0f7f..e55471305c5b 100644
--- a/sdk/nodejs/runtime/closure/createClosure.ts
+++ b/sdk/nodejs/runtime/closure/createClosure.ts
@@ -1546,6 +1546,36 @@ function getBuiltInModules(): Promise<Map<any, string>> {
     }
 }

+/**
+ * Returns true if obj looks like the result of TypeScript's __importStar() helper, i.e. a plain wrapper object where
+ * `default` holds the original module and all other own properties are re-exports from that module.
+ */
+function isImportStarResult(obj: any): obj is { default: unknown } {
+    if (obj == null || typeof obj !== "object" || !("default" in obj)) {
+        return false;
+    }
+    // __importStar creates its result with `var result = {}`, so the prototype is Object.prototype.
+    if (Object.getPrototypeOf(obj) !== Object.prototype) {
+        return false;
+    }
+    const mod = obj.default;
+    if (mod == null) {
+        return false;
+    }
+    // Every re-exported property must also exist on the underlying module
+    let hasReExport = false;
+    for (const k of Object.getOwnPropertyNames(obj)) {
+        if (k === "default" || k === "__esModule") {
+            continue;
+        }
+        if (!(k in mod)) {
+            return false;
+        }
+        hasReExport = true;
+    }
+    return hasReExport;
+}
+
 /**
  * Attempts to find a global name bound to the object, which can be used as a
  * stable reference across serialization.  For built-in modules (i.e. `os`,
@@ -1565,6 +1595,16 @@ async function findNormalizedModuleNameAsync(obj: any): Promise<string | undefin
         return key;
     }

+    // When TypeScript compiles `import * as foo from "foo"` with `module: "nodenext"`, it emits
+    // `__importStar(require("foo"))`. This creates a wrapper object with a `default` property that holds the original
+    // module.
+    if (isImportStarResult(obj)) {
+        const unwrappedKey = modules.get(obj.default);
+        if (unwrappedKey) {
+            return unwrappedKey;
+        }
+    }
+
     // Next, check the Node module require cache, which will store cached values
     // of all non-built-in Node modules loaded by the program so far. _Note_: We
     // don't pre-compute this because the require cache will get populated
diff --git a/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/181-Capture-importStar-wrapped-builtin-module/index.ts b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/181-Capture-importStar-wrapped-builtin-module/index.ts
new file mode 100644
index 000000000000..384abc5379e1
--- /dev/null
+++ b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/181-Capture-importStar-wrapped-builtin-module/index.ts
@@ -0,0 +1,36 @@
+// Copyright 2026, Pulumi Corporation.
+//
+// Licensed under the Apache License, Version 2.0 (the "License");
+// you may not use this file except in compliance with the License.
+// You may obtain a copy of the License at
+//
+//     http://www.apache.org/licenses/LICENSE-2.0
+//
+// Unless required by applicable law or agreed to in writing, software
+// distributed under the License is distributed on an "AS IS" BASIS,
+// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+// See the License for the specific language governing permissions and
+// limitations under the License.
+
+export const description = "Capture __importStar wrapped builtin module";
+
+// Simulate the wrapper that TypeScript emits for `import * as crypto from "crypto"` when compiling with `module:
+// "nodenext"`. The __importStar helper wraps the require() result in a new object with getter properties and a
+// `default` property holding the original module.
+function __importStar(mod: any): any {
+    if (mod && mod.__esModule) return mod;
+    const result: any = {};
+    if (mod != null) {
+        for (const k of Object.getOwnPropertyNames(mod)) {
+            if (k !== "default") {
+                Object.defineProperty(result, k, { enumerable: true, get: () => mod[k] });
+            }
+        }
+    }
+    Object.defineProperty(result, "default", { enumerable: true, value: mod });
+    return result;
+}
+
+const crypto = __importStar(require("crypto"));
+
+export const func = () => crypto;
diff --git a/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/181-Capture-importStar-wrapped-builtin-module/snapshot.txt b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/181-Capture-importStar-wrapped-builtin-module/snapshot.txt
new file mode 100644
index 000000000000..4c005c59182b
--- /dev/null
+++ b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/181-Capture-importStar-wrapped-builtin-module/snapshot.txt
@@ -0,0 +1,12 @@
+exports.handler = __f0;
+const crypto = require("crypto");
+
+function __f0() {
+  return (function() {
+    with({ this: undefined, arguments: undefined }) {
+
+return () => crypto;
+
+    }
+  }).apply(undefined, undefined).apply(this, arguments);
+}
diff --git a/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/182-Object-with-default-builtin-is-not-importStar/index.ts b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/182-Object-with-default-builtin-is-not-importStar/index.ts
new file mode 100644
index 000000000000..a64647fa61e4
--- /dev/null
+++ b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/182-Object-with-default-builtin-is-not-importStar/index.ts
@@ -0,0 +1,22 @@
+// Copyright 2026, Pulumi Corporation.
+//
+// Licensed under the Apache License, Version 2.0 (the "License");
+// you may not use this file except in compliance with the License.
+// You may obtain a copy of the License at
+//
+//     http://www.apache.org/licenses/LICENSE-2.0
+//
+// Unless required by applicable law or agreed to in writing, software
+// distributed under the License is distributed on an "AS IS" BASIS,
+// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+// See the License for the specific language governing permissions and
+// limitations under the License.
+
+export const description = "Object with default builtin is not importStar";
+
+// A plain object that happens to have a `default` property pointing to a builtin module. This should NOT be treated as
+// an __importStar wrapper, instead it should be serialized as a regular object with a `default` property referencing
+// the module.
+const obj = { default: require("crypto") };
+
+export const func = () => obj;
diff --git a/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/182-Object-with-default-builtin-is-not-importStar/snapshot.txt b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/182-Object-with-default-builtin-is-not-importStar/snapshot.txt
new file mode 100644
index 000000000000..525c5692b398
--- /dev/null
+++ b/sdk/nodejs/tests/runtime/testdata/closure-tests/cases/182-Object-with-default-builtin-is-not-importStar/snapshot.txt
@@ -0,0 +1,13 @@
+exports.handler = __f0;
+
+var __obj = {default: require("crypto")};
+
+function __f0() {
+  return (function() {
+    with({ obj: __obj, this: undefined, arguments: undefined }) {
+
+return () => obj;
+
+    }
+  }).apply(undefined, undefined).apply(this, arguments);
+}
PATCH
fi

# Rebuild the SDK so changes are reflected in the bin/ output
cd /workspace/pulumi/sdk/nodejs
yarn run tsc
mkdir -p bin/proto
cp -R proto/. bin/proto/
cp package.json bin/package.json
mkdir -p bin/vendor
cp -R vendor/. bin/vendor/
