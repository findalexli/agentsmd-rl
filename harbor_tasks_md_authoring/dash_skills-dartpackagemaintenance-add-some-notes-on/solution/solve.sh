#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dash-skills

# Idempotency guard
if grep -qF "- **Do Not Amend Released Versions**: Never add new entries to a version header" ".agent/skills/dart-package-maintenance/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/dart-package-maintenance/SKILL.md b/.agent/skills/dart-package-maintenance/SKILL.md
@@ -21,6 +21,26 @@ practices.
 - **Unstable packages**: Use `0.major.minor+patch`.
 - **Recommendation**: Aim for `1.0.0` as soon as the package is stable.
 
+### Pre-Edit Verification
+- **Check Published Versions**: Before modifying `CHANGELOG.md` or
+  `pubspec.yaml`, ALWAYS check the currently released version (e.g., via
+  `git tag` or `pub.dev`).
+- **Do Not Amend Released Versions**: Never add new entries to a version header
+  that corresponds to a released tag.
+- **Increment for New Changes**: If the current version in `pubspec.yaml`
+  matches a released tag, increment the version (e.g., usually to `-wip`) and
+  create a new section in `CHANGELOG.md`.
+
+  - **Consistency**: The `CHANGELOG.md` header must match the new
+    `pubspec.yaml` version.
+
+  - **SemVer Guidelines**:
+    - **Breaking Changes**: Bump Major, reset Minor/Patch
+      (e.g., `2.0.0-wip`, `0.5.0-wip`).
+    - **New Features**: Bump Minor, reset Patch
+      (e.g., `1.1.0-wip`, `0.4.5-wip`).
+    - **Bug Fixes**: Bump Patch (e.g., `1.0.1-wip`).
+
 ### Work-in-Progress (WIP) Versions
 - Immediately after a publish, or on the first change after a publish, update
   `pubspec.yaml` and `CHANGELOG.md` with a `-wip` suffix (e.g., `1.1.0-wip`).
PATCH

echo "Gold patch applied."
