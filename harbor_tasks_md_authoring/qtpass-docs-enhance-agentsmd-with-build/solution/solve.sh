#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "- Use `QCoreApplication::arguments()` instead of raw `argv[]` for CLI parsing (f" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -5,16 +5,24 @@ This file provides guidance for AI agents working on QtPass development.
 ## Build
 
 ```bash
-# Full build
+# Full build (Qt 6)
 qmake6 && make -j4
 
+# Full build (Qt 5 alternative)
+qmake && make -j4
+
 # With tests
 make check
 
-# With coverage
+# With coverage (Qt 6)
 qmake6 -r CONFIG+=coverage
 make -j4
 make lcov
+
+# With coverage (Qt 5 alternative)
+qmake -r CONFIG+=coverage
+make -j4
+make lcov
 ```
 
 ## Linting
@@ -42,6 +50,9 @@ clang-format --style=file -i <source-file>
 
 - **Create branch:** `git checkout -b fix/description`
 - **Commit (always sign):** `git commit -S -m "description"`
+  - Prerequisite: configure Git commit signing (GPG or SSH signing key) before using `-S`.
+  - Verify signing works: `git commit -S --allow-empty -m "test signed commit"` (then reset if needed).
+  - If signing fails, set up your signing key and Git `user.signingkey`/signing format, then retry.
 - **Push:** `git push -u origin branch-name`
 - **Create PR:** `gh pr create --title "description" --body "## Summary\n- details"`
 - **Update with main before merging:**
@@ -53,7 +64,7 @@ clang-format --style=file -i <source-file>
 
 ## Key Conventions
 
-- Use `QCoreApplication::arguments()` instead of raw `argv[]` for CLI parsing
+- Use `QCoreApplication::arguments()` instead of raw `argv[]` for CLI parsing (for proper Unicode handling and cross-platform consistency)
 - Use `QDir::cleanPath()` for cross-platform path normalization
 - Check for null from `screenAt()` before dereferencing
 - Use `tr()` for all user-facing strings
@@ -221,10 +232,10 @@ while (dirObj.exists()) {
 
 The boundary check uses `QDir::cleanPath()` on both paths to prevent sibling-path
 matches (e.g., `/home/user/.password-store2` should not match
-`/home/user/.password-store`). The literal `"/"` is correct here because
-`QDir::cleanPath()` always normalises to forward slashes — using
-`QDir::separator()` would silently break the comparison on Windows where it
-returns `\\`.
+`/home/user/.password-store`). The literal `"/"` is correct here because, in Qt,
+`QDir::cleanPath()` normalises path separators to forward slashes on all
+platforms — using `QDir::separator()` would silently break the comparison on
+Windows where it returns `\\`.
 
 See `Pass::getGpgIdPath` in `src/pass.cpp` for the canonical implementation;
 this pattern supports nested folder inheritance.
PATCH

echo "Gold patch applied."
