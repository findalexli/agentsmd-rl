#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gridlayout-compose

# Idempotency guard
if grep -qF "- Update documentation when the feature is added, removed or changed." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,33 @@
+# Guidelines for AI Agents
+
+## Core Rules
+
+- Update documentation when the feature is added, removed or changed.
+- Verify changes by running tests after making changes.
+- Run `./gradlew apiDump` when the public API is changed.
+
+## Project Structure
+
+- `grid/`: The main library module.
+  - `src/commonMain/`: Main source code for the library.
+  - `src/androidMain/`: Android specific source code.
+  - `src/test/`: Unit tests and snapshot tests.
+- `samples/`: Sample applications.
+  - `shared/`: Shared code module for all sample applications.
+  - `android/`: Android sample application.
+  - `desktop/`: Desktop sample application.
+  - `ios/`: Xcode project for iOS sample application.
+- `docs/`: Documentation.
+
+## Commands
+
+- `./gradlew build`: Build project.
+- `./gradlew test`: Run all test cases.
+- `./gradlew verifyPaparazziDebug`: Run only snapshot tests.
+- `./gradlew recordPaparazziDebug`: Update and create new snapshots.
+- `./gradlew apiDump`: Update public API binary compatibility.
+
+## Commit Style
+
+- Use concise, atomic commit message.
+- Start with capitalized imperative verb.
PATCH

echo "Gold patch applied."
