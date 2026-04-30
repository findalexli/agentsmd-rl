#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dash-skills

# Idempotency guard
if grep -qF "- **[`dart-modern-features`](../dart-modern-features/SKILL.md)**: For idiomatic" ".agent/skills/dart-best-practices/SKILL.md" && grep -qF "- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:" ".agent/skills/dart-checks-migration/SKILL.md" && grep -qF "- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this" ".agent/skills/dart-matcher-best-practices/SKILL.md" && grep -qF "- **[`dart-best-practices`](../dart-best-practices/SKILL.md)**: General code" ".agent/skills/dart-modern-features/SKILL.md" && grep -qF "- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:" ".agent/skills/dart-test-fundamentals/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/dart-best-practices/SKILL.md b/.agent/skills/dart-best-practices/SKILL.md
@@ -36,40 +36,6 @@ ${base64Encode(fullBytes)}
 -----END RSA PRIVATE KEY-----''';
 ```
 
-### Robust extractions of values from a Map with Switch Expressions
-When parsing `Map` structures or JSON (e.g., from `jsonDecode`), use switch
-expressions with object patterns for deep validation and extraction. This is
-clearer and safer than manual `is` checks or `as` casts.
-
-**Avoid (Unsafe Access):**
-```dart
-final json = jsonDecode(stdout);
-if (json is Map &&
-    json['configuration'] is Map &&
-    json['configuration']['properties'] is Map &&
-    json['configuration']['properties']['core'] is Map) {
-  return json['configuration']['properties']['core']['project'] as String?;
-}
-return null;
-```
-
-**Prefer (Deep Pattern Matching):**
-```dart
-return switch (jsonDecode(stdout)) {
-  {
-    'configuration': {
-      'properties': {'core': {'project': final String project}},
-    },
-  } =>
-    project,
-  _ => null,
-};
-```
-
-This pattern cleanly handles deeply nested structures and nullable fields
-without the complexity of verbose `if-else` blocks or the risk of runtime cast
-errors.
-
 ### Line Length
 Avoid lines longer than 80 characters, even in Markdown files and comments.
 This ensures code is readable in split-screen views and on smaller screens
@@ -78,3 +44,9 @@ without horizontal scrolling.
 **Prefer:**
 Target 80 characters for wrapping text. Exceptions are allowed for long URLs
 or identifiers that cannot be broken.
+
+## Related Skills
+
+- **[`dart-modern-features`](../dart-modern-features/SKILL.md)**: For idiomatic
+  usage of modern Dart features like Pattern Matching (useful for deep JSON
+  extraction), Records, and Switch Expressions.
diff --git a/.agent/skills/dart-checks-migration/SKILL.md b/.agent/skills/dart-checks-migration/SKILL.md
@@ -124,3 +124,11 @@ check(it)..isGreaterThan(10)..isLessThan(20);
   migration and you cannot fix it immediately, REVERT that specific change.
 - **Type Safety**: `package:checks` is stricter about types than `matcher`.
   You may need to add explicit `as T` casts or `isA<T>()` checks in the chain.
+
+## Related Skills
+
+- **[`dart-test-fundamentals`](../dart-test-fundamentals/SKILL.md)**: Core
+  concepts for structuring tests, lifecycles, and configuration.
+- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:
+  Best practices for the traditional `package:matcher` that is being migrated
+  away from.
diff --git a/.agent/skills/dart-matcher-best-practices/SKILL.md b/.agent/skills/dart-matcher-best-practices/SKILL.md
@@ -96,3 +96,11 @@ expect(sideEffectState, equals('done')); // Race condition!
     assertions; let matchers handle it.
 3.  **Specific Matchers**: Use the most specific matcher available (e.g.,
     `containsPair` for maps instead of checking keys manually).
+
+## Related Skills
+
+- **[`dart-test-fundamentals`](../dart-test-fundamentals/SKILL.md)**: Core
+  concepts for structuring tests, lifecycles, and configuration.
+- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this
+  skill if you are migrating tests from `package:matcher` to modern
+  `package:checks`.
diff --git a/.agent/skills/dart-modern-features/SKILL.md b/.agent/skills/dart-modern-features/SKILL.md
@@ -233,3 +233,9 @@ Reducing visual noise with inferred shorthand.
 ```dart
 LogLevel currentLevel = .info;
 ```
+
+## Related Skills
+
+- **[`dart-best-practices`](../dart-best-practices/SKILL.md)**: General code
+  style and foundational Dart idioms that predate or complement the modern
+  syntax features.
diff --git a/.agent/skills/dart-test-fundamentals/SKILL.md b/.agent/skills/dart-test-fundamentals/SKILL.md
@@ -111,3 +111,14 @@ timeouts:
 - `dart test`: Run all tests.
 - `dart test test/path/to/file_test.dart`: Run a specific file.
 - `dart test --name "substring"`: Run tests matching a description.
+
+## Related Skills
+
+`dart-test-fundamentals` is the core skill for structuring and configuring
+tests. For writing assertions within those tests, refer to:
+
+- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:
+  Use this if the project sticks with the traditional
+  `package:matcher` (`expect` calls).
+- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this
+  if the project is migrating to the modern `package:checks` (`check` calls).
PATCH

echo "Gold patch applied."
