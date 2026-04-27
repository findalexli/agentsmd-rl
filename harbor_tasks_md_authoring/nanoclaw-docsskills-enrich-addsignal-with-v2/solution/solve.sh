#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "Modern Signal groups use GroupV2. The adapter must extract the group ID from `en" ".claude/skills/add-signal/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-signal/SKILL.md b/.claude/skills/add-signal/SKILL.md
@@ -5,19 +5,115 @@ description: Add Signal channel integration via signal-cli TCP daemon. Native ad
 
 # Add Signal Channel
 
-Adds Signal messaging support via a native adapter that speaks JSON-RPC to a [signal-cli](https://github.com/AsamK/signal-cli) TCP daemon. No Chat SDK bridge, no npm deps — only Node.js builtins.
+Adds Signal messaging support via a native adapter that speaks JSON-RPC to a [signal-cli](https://github.com/AsamK/signal-cli) TCP daemon. No Chat SDK bridge — only Node.js builtins (`node:net`, `node:child_process`, `node:fs`).
+
+Unlike Telegram or Discord, Signal has no bot API. NanoClaw registers as a full Signal account on a dedicated phone number (recommended) or links as a secondary device on your existing number.
 
 ## Prerequisites
 
-`signal-cli` installed and a Signal account linked:
+### Java
 
-- macOS: `brew install signal-cli`
-- Linux: download from [GitHub releases](https://github.com/AsamK/signal-cli/releases)
-- Link your account: `signal-cli -a +1YOURNUMBER link` (follow the QR instructions)
+signal-cli requires Java 17+:
 
-## Install
+```bash
+java -version
+```
+
+If missing:
+- **macOS:** `brew install --cask temurin@17`
+- **Debian/Ubuntu:** `sudo apt-get install -y default-jre`
+- **RHEL/Fedora:** `sudo dnf install -y java-17-openjdk`
+
+Java 17–25 all work.
+
+### signal-cli
+
+- **macOS:** `brew install signal-cli`
+- **Linux:** download the native binary from [GitHub releases](https://github.com/AsamK/signal-cli/releases):
+
+```bash
+SIGNAL_CLI_VERSION=$(curl -fsSL https://api.github.com/repos/AsamK/signal-cli/releases/latest | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'][1:])")
+curl -fsSL "https://github.com/AsamK/signal-cli/releases/download/v${SIGNAL_CLI_VERSION}/signal-cli-${SIGNAL_CLI_VERSION}-Linux-native.tar.gz" \
+  | tar -xz -C ~/.local
+ln -sf ~/.local/signal-cli ~/.local/bin/signal-cli
+signal-cli --version
+```
+
+> The Linux native tarball extracts a single binary directly to `~/.local/signal-cli` (not into a subdirectory). The symlink above puts it on PATH.
+
+## Registration
+
+Two paths. The new-number path is recommended and battle-tested.
+
+### Path A: Register a new number (recommended)
+
+Use a dedicated SIM or VoIP number. NanoClaw owns it entirely.
+
+> **VoIP numbers:** Signal requires SMS verification before voice. Some VoIP providers are blocked even for voice calls. If registration fails with an auth error, try a different provider or a physical SIM.
+
+**Step 1: Solve the CAPTCHA**
+
+Signal requires a CAPTCHA on first registration:
+
+1. Open `https://signalcaptchas.org/registration/generate.html` in a browser
+2. Solve the captcha
+3. Right-click the **"Open Signal"** button → **Copy Link**
+4. The link starts with `signalcaptcha://` — the token is everything after that prefix
+
+**Step 2: Request SMS verification**
 
-NanoClaw doesn't ship channels in trunk. This skill copies the Signal adapter and its tests in from the `channels` branch.
+```bash
+signal-cli -a +1YOURNUMBER register --captcha "PASTE_TOKEN_HERE"
+```
+
+**Step 3: Voice call fallback (if your number can't receive SMS)**
+
+Wait ~60 seconds after the SMS request, then:
+
+```bash
+signal-cli -a +1YOURNUMBER register --voice --captcha "SAME_TOKEN"
+```
+
+Signal calls your number and reads a 6-digit code. The same captcha token is reusable — no need to solve a new one.
+
+> You must request SMS first. Requesting voice immediately fails with `Invalid verification method: Before requesting voice verification…`
+
+**Step 4: Verify**
+
+```bash
+signal-cli -a +1YOURNUMBER verify CODE
+```
+
+No output = success.
+
+**Step 5: Set profile name (optional)**
+
+> ⚠ Stop NanoClaw before running signal-cli commands — the daemon holds an exclusive lock on its data directory while running.
+
+```bash
+# macOS
+launchctl unload ~/Library/LaunchAgents/com.nanoclaw.plist
+signal-cli -a +1YOURNUMBER updateProfile --name "YourBotName"
+# optionally: --avatar /path/to/avatar.jpg
+launchctl load ~/Library/LaunchAgents/com.nanoclaw.plist
+
+# Linux
+systemctl --user stop nanoclaw
+signal-cli -a +1YOURNUMBER updateProfile --name "YourBotName"
+systemctl --user start nanoclaw
+```
+
+### Path B: Link as secondary device
+
+Joins an existing Signal account as a secondary device. Simpler, but NanoClaw shares your personal number.
+
+```bash
+signal-cli -a +1YOURNUMBER link --name "NanoClaw"
+```
+
+This prints a `tsdevice:` URI. Scan it as a QR code on your phone: **Settings → Linked Devices → Link New Device**. QR codes expire in ~30 seconds — re-run if it expires.
+
+## Install
 
 ### Pre-flight (idempotent)
 
@@ -55,7 +151,7 @@ import './signal.js';
 pnpm run build
 ```
 
-No npm packages to install — the adapter uses only Node.js builtins (`node:net`, `node:child_process`, `node:fs`).
+No npm packages to install — the adapter uses only Node.js builtins.
 
 ## Credentials
 
@@ -97,27 +193,73 @@ launchctl kickstart -k gui/$(id -u)/com.nanoclaw
 systemctl --user restart nanoclaw
 ```
 
+## Wiring
+
+### DMs
+
+After the service starts, send any message to the Signal number from your personal Signal app. The router auto-creates a `messaging_groups` row. Then:
+
+```bash
+sqlite3 data/v2.db \
+  "SELECT id, platform_id FROM messaging_groups WHERE channel_type='signal' ORDER BY created_at DESC LIMIT 5"
+```
+
+Pass the `id` to `/init-first-agent` or `/manage-channels` to wire it to an agent group.
+
+### Groups
+
+Add the Signal number to a group from your phone, send any message, then wire the resulting row the same way. For isolated per-group sessions:
+
+```bash
+NOW=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
+sqlite3 data/v2.db "
+INSERT OR IGNORE INTO messaging_group_agents
+  (id, messaging_group_id, agent_group_id, session_mode, priority, created_at)
+VALUES
+  ('mga-'||hex(randomblob(8)), 'mg-GROUPID', 'ag-AGENTID', 'isolated', 0, '$NOW');
+"
+```
+
+### Grant user access
+
+New Signal users (including the owner's Signal identity) are silently dropped with `not_member` until granted access. After the user's first message appears in `messaging_groups`:
+
+```bash
+NOW=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
+sqlite3 data/v2.db "
+INSERT OR REPLACE INTO user_roles (user_id, role, agent_group_id, granted_by, granted_at)
+  VALUES ('signal:UUID', 'owner', NULL, 'system', '$NOW');
+INSERT OR IGNORE INTO agent_group_members (user_id, agent_group_id, added_by, added_at)
+  VALUES ('signal:UUID', 'ag-AGENTID', 'system', '$NOW');
+"
+```
+
+Find the UUID from `messaging_groups.platform_id` or the `users` table.
+
 ## Next Steps
 
 If you're in the middle of `/setup`, return to the setup flow now.
 
-Otherwise, run `/init-first-agent` to create an agent and wire it to your Signal DM, or `/manage-channels` to wire this channel to an existing agent group. Signal is direct-addressable — your phone number is the platform ID.
+Otherwise, run `/init-first-agent` to create an agent and wire it to your Signal DM, or `/manage-channels` to wire this channel to an existing agent group.
 
 ## Channel Info
 
 - **type**: `signal`
-- **terminology**: Signal has "chats" (1:1 DMs) and "groups."
-- **how-to-find-id**: DMs use your phone number (e.g. `+15555550123`). Groups use `group:<groupId>` — find group IDs via `signal-cli -a +1YOURNUMBER listGroups`.
+- **terminology**: Signal has "chats" (1:1 DMs) and "groups"
 - **supports-threads**: no
+- **platform-id-format**:
+  - DM: `signal:{UUID}` — sender's Signal UUID (ACI), **not** their phone number
+  - Group: `signal:{base64GroupId}` — base64-encoded GroupV2 ID
+- **how-to-find-id**: Send a message to the bot, then query `messaging_groups` as shown above
 - **typical-use**: Personal assistant via Signal DMs or small group chats
-- **default-isolation**: One agent per Signal account. Multiple chats with the same operator can share an agent group; groups with other people should typically be separate.
+- **default-isolation**: One agent per Signal account. Multiple chats with the same operator can share an agent group; groups with other people should typically use `isolated` session mode
 
 ### Features
 
 - Markdown formatting — `**bold**`, `*italic*` / `_italic_`, `` `code` ``, ` ```code fence``` `, `~~strike~~`, `||spoiler||` (converted to Signal's offset-based text styles)
 - Quoted replies — `replyTo*` fields populated from Signal quotes
 - Typing indicators — DMs only (Signal doesn't support group typing)
-- Echo suppression — outbound messages are matched on `(platformId, text)` within a 10 s TTL to avoid syncMessage loops
+- Echo suppression — outbound messages matched on `(platformId, text)` within a 10 s TTL to avoid syncMessage loops
 - Note to Self — messages you send to your own account from another device route to the agent as inbound with `isFromMe: true`
 - Voice attachments — detected but not transcribed by default; the agent receives `[Voice Message]` placeholder text. Run `/add-voice-transcription` for local transcription via parakeet-mlx
 
@@ -145,4 +287,32 @@ If you see `Signal daemon not reachable at 127.0.0.1:7583` and `SIGNAL_MANAGE_DA
 
 ### Lost connection mid-session
 
-If you see `Signal channel lost TCP connection to signal-cli daemon` in the logs, the daemon dropped us. There's no auto-reconnect yet — restart the service to re-establish.
+If you see `Signal channel lost TCP connection to signal-cli daemon` in the logs, the daemon dropped the connection. Restart the service to re-establish.
+
+### Messages dropped with `not_member`
+
+The Signal user hasn't been granted membership. See "Grant user access" above. This affects every new Signal user, including the owner's Signal identity — which is a separate user record from their identity on other channels even if it's the same person.
+
+### Captcha required
+
+Signal requires a captcha for new registrations. Go to `https://signalcaptchas.org/registration/generate.html`, solve it, right-click "Open Signal", copy the link, extract the token after `signalcaptcha://`.
+
+### `Invalid verification method: Before requesting voice verification…`
+
+You must request SMS first, wait ~60 seconds, then request voice. Both steps can use the same captcha token.
+
+### Config file in use / daemon lock
+
+signal-cli holds an exclusive lock on its data directory while the daemon is running. Stop NanoClaw before running any `signal-cli` commands directly, then restart afterward.
+
+### Group replies going to DM instead of group
+
+Modern Signal groups use GroupV2. The adapter must extract the group ID from `envelope?.dataMessage?.groupV2?.id` — not `groupInfo?.groupId`, which is GroupV1/legacy. If group messages are routing as DMs, check `src/channels/signal.ts` and confirm the groupId extraction falls through to `groupV2.id`.
+
+### Java not found
+
+Install Java 17+ — see the Prerequisites section above.
+
+### QR code expired (Path B)
+
+QR codes expire in ~30 seconds. Re-run the link command to generate a new one.
PATCH

echo "Gold patch applied."
