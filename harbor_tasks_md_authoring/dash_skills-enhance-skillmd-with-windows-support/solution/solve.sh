#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dash-skills

# Idempotency guard
if grep -qF "When writing CLI applications and tests, ensure compatibility with Windows:" ".agent/skills/dart-cli-app-best-practices/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/dart-cli-app-best-practices/SKILL.md b/.agent/skills/dart-cli-app-best-practices/SKILL.md
@@ -93,6 +93,15 @@ Future<void> main(List<String> arguments) async {
 }
 ```
 
+### Cross-Platform Compatibility (Windows Support)
+When writing CLI applications and tests, ensure compatibility with Windows:
+- **Paths**: Never hardcode path separators like `/`. Use `package:path`'s
+  `p.join` or `p.normalize` to construct paths portably.
+- **File Permissions**: When testing file permission errors, remember that
+  `chmod` is not available on Windows. Use `icacls` on Windows or appropriate
+  mock libraries. Never skip tests on Windows simply because of permission
+  commands if a Windows equivalent exists.
+
 ## 3. Recommended Packages
 
 Use these community-standard packages owned by the [Dart team](https://dart.dev)
PATCH

echo "Gold patch applied."
