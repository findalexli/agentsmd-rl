#!/usr/bin/env bash
set -euo pipefail

cd /workspace/latchkey

# Idempotency guard
if grep -qF "5. **If necessary, ask the user to configure credentials first.** Tell the user " "integrations/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/integrations/SKILL.md b/integrations/SKILL.md
@@ -2,6 +2,18 @@
 name: latchkey
 description: Interact with third-party or self-hosted services (Slack, Google Workspace, Dropbox, GitHub, Linear, Coolify...) using their HTTP APIs on the user's behalf.
 compatibility: Requires node.js, curl and latchkey (npm install -g latchkey). A desktop/GUI environment is required for the browser functionality.
+metadata:
+  openclaw:
+    emoji: "🔑"
+    requires:
+      bins: ["latchkey"]
+    install:
+      - id: npm
+        kind: npm
+        package: latchkey
+        global: true
+        bins: ["latchkey"]
+        label: "Install Latchkey (npm)"
 ---
 
 # Latchkey
@@ -16,11 +28,12 @@ Usage:
 
 1. **Use `latchkey curl`** instead of regular `curl` for supported services.
 2. **Pass through all regular curl arguments** - latchkey is a transparent wrapper.
-3. **Always check for `latchkey services list --viable`** to get a list of currently usable services.
+3. **Check for `latchkey services list`** to get a list of supported services. Use `--viable` to only show the currently configured ones.
 4. **Use `latchkey services info <service_name>`** to get information about a specific service (auth options, credentials status, API docs links, special requirements, etc.).
-5. **If necessary, get or renew credentials first.** Run `latchkey auth browser <service_name>` to open a browser login pop-up window if supported.
-6. **Look for the newest documentation of the desired public API online.** If using the `browser` auth command, avoid bot-only endpoints.
-7. **Do not initiate a new login if the credentials status is `valid` or `unknown`** - the user might just not have the necessary permissions for the action you're trying to do.
+5. **If necessary, ask the user to configure credentials first.** Tell the user to run `latchkey auth set` on the machine where latchkey is installed (using the setCredentialsExample from the `services info` command).
+6. **Alternatively, let the user log in with the browser.** If supported for the given service, run `latchkey auth browser <service_name>` to open a browser login pop-up window.
+7. **Look for the newest documentation of the desired public API online.** If using the `browser` auth command, avoid bot-only endpoints.
+8. **Do not initiate a new login if the credentials status is `valid` or `unknown`** - the user might just not have the necessary permissions for the action you're trying to do.
 
 
 ## Examples
PATCH

echo "Gold patch applied."
