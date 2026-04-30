#!/usr/bin/env bash
set -euo pipefail

cd /workspace/app-store-connect-cli-skills

# Idempotency guard
if grep -qF "- `asc publish appstore` currently supports `--ipa` workflows; for macOS `.pkg`," "skills/asc-release-flow/SKILL.md" && grep -qF "- `asc testflight beta-testers add --app \"APP_ID\" --email \"tester@example.com\" -" "skills/asc-testflight-orchestration/SKILL.md" && grep -qF "- For `.pkg` uploads, `--version` and `--build-number` are required (they are no" "skills/asc-xcode-build/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/asc-release-flow/SKILL.md b/skills/asc-release-flow/SKILL.md
@@ -45,16 +45,20 @@ macOS apps are distributed as `.pkg` files, not `.ipa`.
 See `asc-xcode-build` skill for full build/archive/export workflow.
 
 ### Upload PKG
-Use `xcrun altool` (asc doesn't yet support .pkg uploads directly):
+Upload the exported `.pkg` using `asc`:
 ```bash
-# Ensure API key is in ~/.appstoreconnect/private_keys/
-xcrun altool --upload-app \
-  -f "/path/to/YourApp.pkg" \
-  --type macos \
-  --apiKey "$ASC_KEY_ID" \
-  --apiIssuer "$ASC_ISSUER_ID"
+asc builds upload \
+  --app <APP_ID> \
+  --pkg <PATH_TO_PKG> \
+  --version <VERSION> \
+  --build-number <BUILD_NUMBER> \
+  --wait
 ```
 
+Notes:
+- `--pkg` automatically sets platform to `MAC_OS`.
+- `asc publish appstore` currently supports `--ipa` workflows; for macOS `.pkg`, use `asc builds upload --pkg` + attach/submit steps below.
+
 ### Attach and Submit
 Same as iOS, but use `--platform MAC_OS`:
 ```bash
diff --git a/skills/asc-testflight-orchestration/SKILL.md b/skills/asc-testflight-orchestration/SKILL.md
@@ -14,12 +14,12 @@ Use this skill when managing TestFlight testers, groups, and build distribution.
 
 ## Manage groups and testers
 - Groups:
-  - `asc beta-groups list --app "APP_ID" --paginate`
-  - `asc beta-groups create --app "APP_ID" --name "Beta Testers"`
+  - `asc testflight beta-groups list --app "APP_ID" --paginate`
+  - `asc testflight beta-groups create --app "APP_ID" --name "Beta Testers"`
 - Testers:
-  - `asc beta-testers list --app "APP_ID" --paginate`
-  - `asc beta-testers add --app "APP_ID" --email "tester@example.com" --group "Beta Testers"`
-  - `asc beta-testers invite --app "APP_ID" --email "tester@example.com"`
+  - `asc testflight beta-testers list --app "APP_ID" --paginate`
+  - `asc testflight beta-testers add --app "APP_ID" --email "tester@example.com" --group "Beta Testers"`
+  - `asc testflight beta-testers invite --app "APP_ID" --email "tester@example.com"`
 
 ## Distribute builds
 - `asc builds add-groups --build "BUILD_ID" --group "GROUP_ID"`
diff --git a/skills/asc-xcode-build/SKILL.md b/skills/asc-xcode-build/SKILL.md
@@ -70,17 +70,20 @@ xcodebuild -exportArchive \
   -allowProvisioningUpdates
 ```
 
-### 3. Upload PKG
-macOS apps export as `.pkg` files. Use `xcrun altool`:
+### 3. Upload PKG with asc
+macOS apps export as `.pkg` files. Upload with `asc`:
 ```bash
-xcrun altool --upload-app \
-  -f "/tmp/YourMacAppExport/YourApp.pkg" \
-  --type macos \
-  --apiKey "$ASC_KEY_ID" \
-  --apiIssuer "$ASC_ISSUER_ID"
+asc builds upload \
+  --app "APP_ID" \
+  --pkg "/tmp/YourMacAppExport/YourApp.pkg" \
+  --version "1.0.0" \
+  --build-number "123"
 ```
 
-Note: The API key file must be in `~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8`
+Notes:
+- `--pkg` automatically sets platform to `MAC_OS`.
+- For `.pkg` uploads, `--version` and `--build-number` are required (they are not auto-extracted like IPA uploads).
+- Add `--wait` if you want to wait for build processing to complete.
 
 ## Build Number Management
 
PATCH

echo "Gold patch applied."
