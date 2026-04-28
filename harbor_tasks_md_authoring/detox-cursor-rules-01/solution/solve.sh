#!/usr/bin/env bash
set -euo pipefail

cd /workspace/detox

# Idempotency guard
if grep -qF "- Minimize comments usage, especially in-line ones. Leave comments where things " ".cursor/rules/detox-idomatic.mdc" && grep -qF "Note: `jest.mock()` must still be called at the module level (for hoisting), but" ".cursor/rules/detox-unittests.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/detox-idomatic.mdc b/.cursor/rules/detox-idomatic.mdc
@@ -0,0 +1,8 @@
+---
+description: Rules to help Cursor write code that is more Detox idomatic
+globs: *.js
+alwaysApply: false
+---
+- Whenever an Error needs to be thrown, prefer throwing a DetoxRuntimeError with a proper message and hint.
+
+- Minimize comments usage, especially in-line ones. Leave comments where things are exceptionally unclear for some reason.
diff --git a/.cursor/rules/detox-unittests.mdc b/.cursor/rules/detox-unittests.mdc
@@ -0,0 +1,62 @@
+---
+Description: Rules to help Cursor write unit tests code that aligns with the project's standards
+globs: *.test.js,*.test.ts
+alwaysApply: false
+---
+# Project Rules
+
+## Jest Unit Testing
+
+In Jest unit test files, **never perform mocking globally**. Instead, perform all mocks inside the `beforeEach()` section.
+
+### Rationale
+- Keeps test setup centralized and visible
+- Ensures mocks are reset between tests
+- Makes test dependencies explicit
+- Prevents test pollution from global mocks
+
+### Example
+
+❌ **Don't do this:**
+```javascript
+const mockSleep = jest.fn().mockResolvedValue(undefined);
+jest.mock('../../../../utils/sleep', () => mockSleep);
+
+describe('MyClass', () => {
+  // ...
+});
+```
+
+✅ **Do this instead:**
+```javascript
+describe('MyClass', () => {
+  let mockSleep;
+
+  beforeEach(() => {
+    jest.mock('../../../../utils/sleep');
+    mockSleep = require('../../../../utils/sleep');
+    mockSleep.mockResolvedValue(undefined);
+
+// ... other setup
+  });
+});
+```
+
+Alternatively, in cases where jest.mock() doesn't work well out of the box, this can be performed too:
+
+```javascript
+  beforeEach(() => {
+    jest.mock('../../../../utils/sleep', () => jest.fn().mockResolvedValue(undefined));
+    mockSleep = require('../../../../utils/sleep');
+  });
+
+  // Or if the sleep js module actually exports an object:
+  beforeEach(() => {
+    jest.mock('../../../../utils/sleep', () => ({
+      sleep: jest.fn().mockResolvedValue(undefined),
+    }));
+    mockSleep = require('../../../../utils/sleep');
+  });
+```
+
+Note: `jest.mock()` must still be called at the module level (for hoisting), but all mock configuration should happen in `beforeEach()`.
PATCH

echo "Gold patch applied."
