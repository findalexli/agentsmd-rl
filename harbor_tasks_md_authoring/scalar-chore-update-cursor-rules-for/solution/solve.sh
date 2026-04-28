#!/usr/bin/env bash
set -euo pipefail

cd /workspace/scalar

# Idempotency guard
if grep -qF "* Do not use nested describe() blocks. Keep tests flat within the single describ" ".cursor/rules/tests.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/tests.mdc b/.cursor/rules/tests.mdc
@@ -1,6 +1,6 @@
 ---
 description: Write awesome tests
-globs: *.test.ts,*.spec.ts
+globs: *.test.ts,*.spec.ts,*.e2e-spec.ts,*.e2e.ts
 alwaysApply: false
 ---
 # Writing Tests
@@ -16,13 +16,12 @@ You write tests that are clear, maintainable, and thorough. You optimize for rea
   * Each test file matches the name of the file it tests. Example: If the code is in custom-function.ts, the test file should be named custom-function.test.ts.
   * The test file is located in the same folder as the file under test. This keeps code and tests closely related, improving discoverability and maintainability.
 * Minimize mocking. Only mock when absolutely necessary. Prefer refactoring the code under test to make mocking unnecessary. Aim for simpler, pure functions that are easier to test without mocks.
-* Every test file has a top-level describe().
+* Every test file has a single top-level describe().
   * The top-level describe() matches the file name under test. Example: describe('custom-function') for custom-function.test.ts.
-	*	Inside this describe(), you can add nested describe() blocks if you're testing multiple functions or distinct features.
-	* Deeper nesting is fine if it improves clarity.
-	*	Use it() for individual tests.
-	*	Keep descriptions concise and direct.
-	*	Do not start with “should.”
+  * Do not use nested describe() blocks. Keep tests flat within the single describe().
+  * Use it() for individual tests.
+  * Keep test descriptions concise and direct.
+  * Do not start test descriptions with "should."
     ✅ it('generates a slug from the title')
     ❌ it('should generate a slug from the title')
 
@@ -63,19 +62,24 @@ You write tests that are clear, maintainable, and thorough. You optimize for rea
 
 ```ts
 import { describe, it, expect } from 'vitest'
-import { generateSlug } from './custom-function'
+import { generateSlug, doSomething } from './custom-lib'
 
-describe('custom-lib', () => {
-  describe('generateSlug', () => {
-    it('generates a slug from the title', () => {
-      const result = generateSlug('Hello World')
-      expect(result).toBe('hello-world')
-    })
+describe('generateSlug', () => {
+  it('generates a slug from the title', () => {
+    const result = generateSlug('Hello World')
+    expect(result).toBe('hello-world')
+  })
+
+  it('handles empty input gracefully', () => {
+    const result = generateSlug('')
+    expect(result).toBe('')
+  })
+})
 
-    it('handles empty input gracefully', () => {
-      const result = generateSlug('')
-      expect(result).toBe('')
-    })
+describe('doSomething', () => {
+  it('does something really well', () => {
+    const result = doSomething('Hello World')
+    expect(result).toBe('hello-world')
   })
 })
 ```
PATCH

echo "Gold patch applied."
