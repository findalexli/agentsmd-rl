#!/usr/bin/env bash
set -euo pipefail

cd /workspace/divine-mobile

# Idempotency guard
if grep -qF "Extracting into packages improves CI speed because only the affected package's w" ".claude/rules/architecture.md" && grep -qF "Transitional or temporary code (feature flags, compatibility shims, workarounds " ".claude/rules/code_style.md" && grep -qF "Simple derivations (null checks, string formatting, boolean flags) are fine as g" ".claude/rules/state_management.md" && grep -qF "When extracting code into a new package (client, repository, utility), include t" ".claude/rules/testing.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/architecture.md b/.claude/rules/architecture.md
@@ -161,6 +161,15 @@ my_app/
 
 Each layer abstracts the underlying layers' implementation details. Avoid indirect dependencies between layers. The implementation details should not leak between the layers.
 
+### When to Extract into a Package
+
+Extract code into a dedicated package when:
+- A repository or client is reused across multiple features
+- A service has grown large enough to slow down CI (each package gets its own targeted CI workflow)
+- The code has no dependency on the app's `lib/` layer
+
+Extracting into packages improves CI speed because only the affected package's workflow runs on changes, rather than the full mobile test suite.
+
 ## Dependency Graph
 
 Data should only flow from the bottom up, and a layer can only access the layer directly beneath it.
diff --git a/.claude/rules/code_style.md b/.claude/rules/code_style.md
@@ -107,6 +107,47 @@ Group related constants together so they are easy to find and update in one plac
 
 ---
 
+## Latest Dependency Versions
+
+When adding a new dependency to `pubspec.yaml`, always use the latest stable version. Don't copy version constraints from older packages without checking for updates.
+
+```yaml
+# Good — checked pub.dev for latest
+very_good_analysis: ^10.2.0
+
+# Bad — copied from another package without checking
+very_good_analysis: ^6.0.0
+```
+
+---
+
+## PR Scope
+
+Pull requests should only include changes directly related to the task. Remove unrelated file modifications (stale lock files, unrelated docs, formatting changes in untouched files) before requesting review.
+
+If you discover something unrelated that needs fixing, create a separate PR or issue for it.
+
+---
+
+## Temporary Code
+
+Transitional or temporary code (feature flags, compatibility shims, workarounds for in-progress migrations) must include a `// TODO(#issue):` comment referencing a tracking issue for its removal. Code without a removal plan tends to become permanent.
+
+```dart
+// Good — linked to a tracking issue
+// TODO(#2854): Remove this fallback after unified search ships
+if (useOldSearch) {
+  return _legacySearch(query);
+}
+
+// Bad — no indication this is temporary or when to remove it
+if (useOldSearch) {
+  return _legacySearch(query);
+}
+```
+
+---
+
 ## Dart Best Practices
 
 ### Null Safety
diff --git a/.claude/rules/state_management.md b/.claude/rules/state_management.md
@@ -337,6 +337,24 @@ class CreateAccountState extends Equatable {
 }
 ```
 
+### Getters vs Stored State: When Computation Is Expensive
+
+Simple derivations (null checks, string formatting, boolean flags) are fine as getters. However, if the computation is expensive — sorting, filtering, or transforming a list — store the result as a field in state rather than recomputing it on every access.
+
+```dart
+// Good — cheap derivation, getter is fine
+bool get isValid => name?.isNotEmpty == true;
+
+// Bad — expensive list operation as a getter, recomputed on every access
+List<Video> get sortedVideos =>
+    videos.toList()..sort((a, b) => b.date.compareTo(a.date));
+
+// Good — computed once at emit time and stored in state
+emit(state.copyWith(
+  sortedVideos: videos.toList()..sort((a, b) => b.date.compareTo(a.date)),
+));
+```
+
 ---
 
 ## State Handling: Enum vs Sealed Classes
diff --git a/.claude/rules/testing.md b/.claude/rules/testing.md
@@ -4,6 +4,17 @@ Goal: 100% test coverage on all projects. Tests reduce bugs, encourage clean cod
 
 ---
 
+## New and Extracted Packages Must Ship with Tests
+
+When extracting code into a new package (client, repository, utility), include test coverage in the same PR. Do not defer tests to a follow-up — the extraction PR is incomplete without them.
+
+At minimum, cover:
+- All public methods on the main class
+- Error/edge cases for network or I/O operations
+- Model serialization if the package defines models
+
+---
+
 ## Test Organization
 
 ### File Structure
PATCH

echo "Gold patch applied."
