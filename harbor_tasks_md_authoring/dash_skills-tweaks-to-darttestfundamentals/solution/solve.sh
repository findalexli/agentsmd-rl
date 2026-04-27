#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dash-skills

# Idempotency guard
if grep -qF "- **NOTE**: DO NOT remove groups when doing a cleanup on existing code you" ".agent/skills/dart-test-fundamentals/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/dart-test-fundamentals/SKILL.md b/.agent/skills/dart-test-fundamentals/SKILL.md
@@ -11,7 +11,7 @@ license: Apache-2.0
 ## When to use this skill
 Use this skill when:
 - Writing new test files.
-- structuring test suites with `group`.
+- Structuring test suites with `group`.
 - Configuring test execution via `dart_test.yaml`.
 - Understanding test lifecycle methods.
 
@@ -33,9 +33,12 @@ Use this skill when:
     (e.g., `group('MyClient', ...)`).
   - **Avoid Single Groups**: Do not wrap all tests in a file with a single
     `group` call if it's the only one.
+    - **NOTE**: DO NOT remove groups when doing a cleanup on existing code you
+      didn't create unless explicitly asked to. This can cause a LOT of churn
+      in the DIFF that most engineers won't want!
 
-- **Naming Tests**:
-  - Avoid redundant "test" prefixes.
+- **Naming Tests** `test('test name here',`:
+  - Avoid redundant "test" prefixes. Use `group` instead.
   - Include the expected behavior or outcome in the description (e.g.,
     `'throws StateError'` or `'adds API key to URL'`).
   - Descriptions should read well when concatenated with their group name.
@@ -62,7 +65,39 @@ Use this skill when:
 - Use `setUp` for resetting state to ensure test isolation.
 - Avoid sharing mutable state between tests without resetting it.
 
-### 3. Configuration (`dart_test.yaml`)
+### 3. Cleaning Up Resources
+
+- To clean up resources created WITHIN the `test` body, consider using
+  `addTearDown` instead of a `try-finally` block.
+
+**Avoid:**
+```dart
+test('can create and delete a file', () {
+  final file = File('temp.txt');
+  try {
+    file.writeAsStringSync('hello');
+    expect(file.readAsStringSync(), 'hello');
+  } finally {
+    if (file.existsSync()) file.deleteSync();
+  }
+});
+```
+
+**Prefer:**
+```dart
+test('can create and delete a file', () {
+  final file = File('temp.txt');
+  // Register teardown immediately after resource creation intent
+  addTearDown(() {
+    if (file.existsSync()) file.deleteSync();
+  });
+
+  file.writeAsStringSync('hello');
+  expect(file.readAsStringSync(), 'hello');
+});
+```
+
+### 4. Configuration (`dart_test.yaml`)
 
 The `dart_test.yaml` file configures the test runner. Common configurations
 include:
@@ -102,7 +137,7 @@ timeouts:
   2x # Double the default timeout
 ```
 
-### 4. File Naming
+### 5. File Naming
 - Test files **must** end in `_test.dart` to be picked up by the test runner.
 - Place tests in the `test/` directory.
 
PATCH

echo "Gold patch applied."
