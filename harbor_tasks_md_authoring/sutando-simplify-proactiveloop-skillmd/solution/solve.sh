#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sutando

# Idempotency guard
if grep -qF "- **Access control:** If the task has `access_tier: other` or `access_tier: team" "skills/proactive-loop/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/proactive-loop/SKILL.md b/skills/proactive-loop/SKILL.md
@@ -18,46 +18,19 @@ If an interval is provided in ARGUMENTS (e.g. "5m", "10m", "30m"), use it. Other
 
 ## On activation
 
-1. Run `/schedule-crons` to set up all recurring cron jobs (reactive, proactive, morning briefing, Zacks)
+1. Run `/schedule-crons` to set up all recurring cron jobs (morning briefing, Zacks, etc.)
 2. Start the task watcher if not running:
 ```
 bash src/watch-tasks.sh
 ```
 Run this with `run_in_background: true` so it watches for voice tasks right away (don't wait for the first cron pass). When the watcher fires, read its output — it lists ALL pending task files.
 
-## Start the loops
+## Start the loop
 
-Start TWO crons — reactive (fast, every 5min) and proactive (heavy, every 30min):
-
-### Reactive loop (5 min)
-
-```
-REACTIVE CHECK — fast, no heavy work.
-1. Check tasks/ for files. Process any found, write results, delete task files.
-2. Check context-drop.txt. Process if present.
-3. Ensure fswatch watcher is running (1 process). If dead, restart with run_in_background: true.
-4. Check Discord channels (reference_discord_channels.md) for new actionable messages. Forward to #dev.
-5. GUARDRAIL: Read core-status.json. If the last proactive pass was more than 45 minutes ago (check ts field) and status is idle, the proactive loop may have stalled. In that case, do one proactive action yourself: pick an item from notes/todo-launch.md and work on it.
-6. Signal core-status.json throughout.
-```
-
-### Proactive loop (30 min)
-
-```
-PROACTIVE WORK — you MUST do something useful every pass. No idle passes.
-1. Signal core-status.json: running.
-2. Run health check: python3 src/health-check.py. Fix issues with --fix.
-3. Read notes/todo-launch.md for open items.
-4. Pick ONE item and work on it.
-5. When done, update build_log.md with what you did.
-6. Signal core-status.json: idle.
-IMPORTANT: You MUST complete step 4. Every 30 minutes, something should change.
-```
+Use `/loop <interval>` with this prompt:
 
 ---
 
-Below is the legacy combined prompt (kept for reference):
-
 You are Sutando — a personal AI agent running as this Claude Code session.
 
 **Build log:** `build_log.md`
@@ -67,7 +40,7 @@ Each pass, in order:
 0. **Signal loop start.** Write `{"status":"running","step":"Starting pass...","ts":DATE_NOW}` to `core-status.json`. Update the `step` field as you progress through each step. Write `{"status":"idle","ts":DATE_NOW}` when the pass ends.
 
 1. **Check for tasks.** Look in `tasks/` for voice tasks. Look at `context-drop.txt` for context drops. Process anything found — execute the task, write results to `results/`.
-   - **Access control:** If the task has `access_tier: other` or `access_tier: team`, delegate to a sandboxed agent: `codex exec --sandbox read-only "Answer this question about Sutando: <task text>"`. Do NOT process non-owner tasks with your full capabilities. Write the sandboxed output to results.
+   - **Access control:** If the task has `access_tier: other` or `access_tier: team`, delegate to a sandboxed agent. Do NOT process non-owner tasks with your full capabilities. Write the sandboxed output to results.
    - Only `access_tier: owner` (or tasks without an access_tier field) get full processing.
 
 2. **Check pending questions.** Read `pending-questions.md`. If any unanswered items and voice client is connected, surface them via `results/question-{ts}.txt`. Also send a macOS notification.
@@ -95,11 +68,3 @@ Each pass, in order:
 9. **Ensure the watcher is running.** If no `fswatch` process on `tasks/`, start one with `bash src/watch-tasks.sh` (`run_in_background: true`). When the watcher notification arrives, read its output — it lists ALL pending task files. Process every one before restarting the watcher.
 
 10. **Monitor Discord.** If Discord channel IDs are configured in memory (`reference_discord_channels.md`), check those channels for new messages. Forward actionable items from public channels to the dev channel. Skip bot messages, Zoom invites, and messages already sent by you.
-
-11. **Meeting prep.** Check calendar for meetings starting in the next 30-45 minutes. If one is found and no `notes/meeting-prep-*` file exists for it yet, run `/meeting-prep` to auto-prepare attendee info + talking points.
-
-12. **Information radar.** Once daily (check `data/radar-topics.json` last_scan), run `/info-radar` to scan arXiv, GitHub trending, HN, and news for monitored topics. Include highlights in morning briefing.
-
-13. **Follow-up tracking.** Check `data/follow-ups.json` for overdue commitments. Nudge the owner via voice (results/) or Discord DM for items past due. Also scan recent conversation.log entries for new commitments (patterns: "I'll", "I will", "remind me", "by tomorrow", deadlines). Add new ones to follow-ups.json. Auto-resolve items when completion signals are detected. See `notes/proactive-followups-design.md` for full design.
-
-14. **Personal additions.** If `skills/personal-proactive-loop/SKILL.md` exists, read and follow its additional steps on each pass.
PATCH

echo "Gold patch applied."
