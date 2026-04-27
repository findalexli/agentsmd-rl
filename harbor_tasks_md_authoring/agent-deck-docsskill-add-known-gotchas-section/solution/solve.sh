#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-deck

# Idempotency guard
if grep -qF "If `~/.agent-deck/skills/sources.toml` (or other config files) were copied verba" "skills/agent-deck/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/agent-deck/SKILL.md b/skills/agent-deck/SKILL.md
@@ -341,6 +341,89 @@ $SKILL_DIR/../session-share/scripts/import.sh ~/Downloads/session-file.json
 2. **Restart after MCP attach:** Always run `session restart` after `mcp attach`
 3. **Never poll from other agents** - can interfere with target session
 
+## Known Gotchas (v1.7.0+)
+
+Friction points discovered during real usage. Work around them per the patterns below.
+
+### `session send --no-wait` can leave prompts typed-but-not-submitted
+
+On a freshly-launched Claude session, `agent-deck session send --no-wait <id> "..."` may paste the message into the input buffer before Claude is fully ready, leaving it TYPED but not SUBMITTED. Classic race.
+
+**Workaround (always safe):**
+```bash
+agent-deck -p <profile> session send <id> "..." --no-wait -q
+sleep 3
+# Get the tmux session name and send Enter to submit
+TMUX=$(agent-deck -p <profile> session show --json <id> | jq -r .tmux_session)
+tmux send-keys -t "$TMUX" Enter
+```
+
+The Enter is idempotent — if already submitted, it's just a no-op newline. Use this pattern every time you `session send --no-wait` to a freshly-launched session.
+
+**Alternative:** omit `--no-wait` so the built-in 60s readiness wait kicks in before submitting.
+
+### Replacing the binary while agent-deck is running (`text file busy`)
+
+If `/usr/local/bin/agent-deck` is a symlink to a build artifact and the binary is currently running (any tmux session, any daemon), a direct `cp` over it fails with `Text file busy`.
+
+**Workaround — move-then-copy (keeps running processes on the old inode):**
+```bash
+INSTALL=$(which agent-deck)
+TARGET=$(readlink -f "$INSTALL")
+go build -ldflags "-X main.Version=X.Y.Z" -o /tmp/agent-deck-new ./cmd/agent-deck
+mv "$TARGET" "$TARGET.old"
+cp /tmp/agent-deck-new "$TARGET" && chmod +x "$TARGET"
+agent-deck --version    # verify
+rm "$TARGET.old"
+```
+
+Kernel tracks inodes, not names. Running processes keep a reference to the renamed inode; new invocations resolve through the original name to the new inode.
+
+### Cross-machine config drift (macOS ↔ Linux)
+
+If `~/.agent-deck/skills/sources.toml` (or other config files) were copied verbatim from a macOS machine, paths like `/Users/<name>/` won't exist on Linux (should be `/home/<user>/`). The symptom: `agent-deck skill list` returns "No skills found" while the pool directory is clearly populated.
+
+**Check & fix:**
+```bash
+grep -n "/Users/" ~/.agent-deck/skills/sources.toml
+# If any matches, substitute the Linux home path:
+sed -i "s|/Users/<mac-user>|$HOME|g" ~/.agent-deck/skills/sources.toml
+```
+
+### Channel subscription for conductor/bot sessions (v1.7.0+)
+
+For a session to receive Telegram/Discord/Slack messages as conversation turns (not just as MCP tool calls), it MUST be started with `--channels <plugin-id>`. Use the first-class field:
+
+```bash
+# At creation (preferred):
+agent-deck -p personal add --channel plugin:telegram@claude-plugins-official -c claude -t my-bot /path
+
+# Or after creation, then restart:
+agent-deck -p personal session set my-bot channels plugin:telegram@claude-plugins-official
+agent-deck -p personal session restart my-bot
+```
+
+The `channels` field persists and every `session start` / `session restart` rebuilds the claude invocation with `--channels`. Do NOT rely on `.mcp.json` telegram entries — those load the plugin as a regular MCP (tools only), not a channel (inbound delivery).
+
+**Note — v1.7.0 display bug:** `agent-deck session show --json <id>` currently omits the `channels` field (fix pending). `agent-deck list --json | jq '.[] | select(.id==<id>)'` shows it correctly. Data is persisted fine regardless.
+
+### Many competing telegram pollers after multiple session starts
+
+Telegram's Bot API `getUpdates` is single-consumer per bot token. If N Claude sessions all load the telegram plugin, N `bun` pollers race for messages — deliveries land in whichever wins, not where you want them.
+
+**Correct topology:** exactly ONE session loads the telegram channel plugin (normally the conductor, via `--channels` at start-time). All other sessions should NOT have telegram in their enabled plugins.
+
+**Disable globally:** in `~/.claude/settings.json`:
+```json
+"enabledPlugins": {
+  "telegram@claude-plugins-official": false
+}
+```
+
+**Enable per-session:** via `--channel` on the specific session that should receive messages. See "Channel subscription" above.
+
+**Debug:** `pgrep -af "bun.*telegram" | wc -l` should return 1. Anything higher means a race. Kill extras: `pkill -f "bun.*telegram"` then restart only the intended session.
+
 ## References
 
 - [cli-reference.md](references/cli-reference.md) - Complete CLI command reference
PATCH

echo "Gold patch applied."
