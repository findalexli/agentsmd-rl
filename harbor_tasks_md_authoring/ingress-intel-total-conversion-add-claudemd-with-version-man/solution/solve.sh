#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ingress-intel-total-conversion

# Idempotency guard
if grep -qF "- **Minor version** (0.3.4 \u2192 0.4.0): New features, API changes, significant enha" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,44 @@
+# Claude Commands for IITC-CE
+
+## Version Management
+
+### Update Plugin and Core Versions
+
+Command: `/version-update` or simply ask Claude to "update versions"
+
+This command will:
+
+1. **Check plugin changes since last release**:
+   - Find the last release commit (search for "release" in commit messages)
+   - Check git history for each plugin since last release
+   - Identify plugins that have changes but haven't had version bumps
+
+2. **Update plugin versions**:
+   - For each changed plugin, determine version increment based on change type:
+     - **Patch version** (0.3.4 → 0.3.5): Bug fixes, eslint fixes, small improvements
+     - **Minor version** (0.3.4 → 0.4.0): New features, API changes, significant enhancements
+   - Add changelog entries describing the changes with appropriate detail level
+
+3. **Update core version**:
+   - Check `core/` directory changes since last release
+   - Increment minor version in `core/total-conversion-build.js` (e.g., 0.40.0 → 0.41.0)
+   - Add changelog entries for core improvements
+   - Focus on user-visible changes and bug fixes
+
+4. **Update mobile app version**:
+   - Update `versionName` in `mobile/app/build.gradle` to match core version
+   - Change from `versionName "0.40.0"` to `versionName "0.41.0"`
+
+### Process Steps:
+1. `git log --oneline [last-release-commit]..HEAD -- plugins/[plugin-name].js`
+2. Check if version in plugin header needs updating
+3. Add concise changelog entries (like "Fix portal snap positioning bug")
+4. `git log --oneline [last-release-commit]..HEAD -- core/`
+5. Update core version and changelog
+6. Exclude translation commits and mobile-specific changes from core changelog
+
+### Example Changelog Entries:
+- **Plugin**: `'Fix portal snap positioning bug'`
+- **Core**: `'Fix RegionScore tooltip HTML rendering'`, `'Update MODs display colors'`
+
+Keep descriptions concise and user-focused, avoiding technical implementation details.
\ No newline at end of file
PATCH

echo "Gold patch applied."
