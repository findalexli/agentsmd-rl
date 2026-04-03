#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if [ -f packages/playwright-cli-stub/playwright-cli-stub.js ]; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/package.json b/package.json
index 65ef07ae16732..1e3c30d3dee5d 100644
--- a/package.json
+++ b/package.json
@@ -44,7 +44,6 @@
     "check-deps": "node utils/check_deps.js",
     "build-android-driver": "./utils/build_android_driver.sh",
     "innerloop": "playwright run-server --reuse-browser",
-    "playwright-cli": "node packages/playwright/lib/cli/client/cli.js",
     "test-playwright-cli": "playwright test --config=tests/mcp/playwright.config.ts --project=chrome cli-",
     "playwright-cli-readme": "node utils/generate_cli_help.js --readme"
   },
diff --git a/packages/playwright-cli-stub/package.json b/packages/playwright-cli-stub/package.json
new file mode 100644
index 0000000000000..a56ea13e2a5b6
--- /dev/null
+++ b/packages/playwright-cli-stub/package.json
@@ -0,0 +1,8 @@
+{
+  "name": "playwright-cli-stub",
+  "version": "0.0.0",
+  "private": true,
+  "bin": {
+    "playwright-cli": "playwright-cli-stub.js"
+  }
+}
diff --git a/packages/playwright-cli-stub/playwright-cli-stub.js b/packages/playwright-cli-stub/playwright-cli-stub.js
new file mode 100755
index 0000000000000..fca4ff77aab06
--- /dev/null
+++ b/packages/playwright-cli-stub/playwright-cli-stub.js
@@ -0,0 +1,23 @@
+#!/usr/bin/env node
+/**
+ * Copyright (c) Microsoft Corporation.
+ *
+ * Licensed under the Apache License, Version 2.0 (the 'License");
+ * you may not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the License for the specific language governing permissions and
+ * limitations under the License.
+ */
+
+const { program } = require('playwright/lib/cli/client/program');
+
+program().catch(e => {
+  console.error(e.message);
+  process.exit(1);
+});
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index 2940cac07928b..99f5884333c22 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -216,19 +216,16 @@ playwright-cli kill-all

 ## Installation

-If `playwright-cli` is not available, install it globally:
+If global `playwright-cli` command is not available, try a local version via `npx playwright-cli`:

 ```bash
-npm install -g @playwright/cli@latest
+npx playwright-cli --version
 ```

-Once installed, `playwright-cli` will be available as a global command.
-
-Alternatively, install the package locally and use `npx` to run without a global install. This is useful for hermetic environments, but adds a slight `npx` overhead on each command execution:
+When local version is available, use `npx playwright-cli` in all commands. Otherwise, install `playwright-cli` as a global command:

 ```bash
-npx playwright-cli open https://example.com
-npx playwright-cli click e1
+npm install -g @playwright/cli@latest
 ```

 ## Example: Form submission

PATCH

echo "Patch applied successfully."
