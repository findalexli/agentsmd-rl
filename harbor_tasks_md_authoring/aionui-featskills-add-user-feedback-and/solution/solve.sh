#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "| Attachment type | Name / MIME pattern             | Analysis method           " ".claude/skills/fix-sentry/SKILL.md" && grep -qF "Total: N fixed (PR created), F from feedback, P pending review, M already fixed," ".claude/skills/fix-sentry/references/report-template.md" && grep -qF "| Category          | Criteria                                                  " ".claude/skills/fix-sentry/references/triage-rules.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/fix-sentry/SKILL.md b/.claude/skills/fix-sentry/SKILL.md
@@ -2,7 +2,8 @@
 name: fix-sentry
 description: |
   Auto-fix high-frequency Sentry issues: fetch issues > N occurrences, analyze stack traces,
-  fix code, create GitHub issues, and submit PRs.
+  fix code, create GitHub issues, and submit PRs. Supports user feedback issues (event.type
+  "default") with attachment analysis (logs, screenshots) when include_feedback=true.
   Use when: (1) User says "/fix-sentry", (2) User asks to fix Sentry issues.
 ---
 
@@ -212,25 +213,92 @@ never in parallel. If you hit a 429, wait a moment and retry.
 Extract:
 
 - Error message and type
+- Event type (`event.type` — `error`, `default`, etc.)
 - Stack trace (file paths, line numbers, function names)
 - First/last seen timestamps
 - Release version(s) affected
 - Frequency and affected users count
 
+#### Step 1.5b: Attachment Analysis
+
+For issues where `event.type` is `default` (user feedback) **or** stack traces are absent,
+check for attachments that may contain diagnostic information.
+
+**When to run:** After Step 1.5, for any issue group that meets either condition:
+
+- `event.type` is `default` (user feedback / bug report)
+- No usable stack trace was extracted in Step 1.5
+
+**Prerequisite:** Only runs when `include_feedback=true` is set for `event.type: default` issues.
+Issues without stack traces are always eligible regardless of this flag.
+
+**Procedure:**
+
+1. **Get events for the issue** (if not already fetched):
+
+   ```
+   mcp__sentry__list_issue_events(
+     issueUrl="<sentry-url>",
+     limit=3
+   )
+   ```
+
+2. **List attachments** for each event:
+
+   ```
+   mcp__sentry__get_event_attachment(
+     projectSlug="<project>",
+     eventId="<eventId>"
+   )
+   ```
+
+3. **Download and analyze attachments by type:**
+
+   | Attachment type | Name / MIME pattern             | Analysis method                                                           |
+   | --------------- | ------------------------------- | ------------------------------------------------------------------------- |
+   | Logs            | `logs.gz`, `*.log`, `*.txt`     | Download → decompress → search for error patterns, stack traces, warnings |
+   | Screenshots     | `*.png`, `*.jpg`, `screenshot*` | Download → use vision to identify UI state, error dialogs, frozen screens |
+   | Config / state  | `*.json`, `*.xml`               | Download → check for misconfigurations                                    |
+
+   ```
+   mcp__sentry__get_event_attachment(
+     projectSlug="<project>",
+     eventId="<eventId>",
+     attachmentId="<attachmentId>"
+   )
+   ```
+
+4. **Extract diagnostic signals from logs:**
+   - Error / Warning lines (`error`, `warn`, `fatal`, `crash`, `EPIPE`, etc.)
+   - Stack traces embedded in log output
+   - Performance indicators (memory usage, CPU spikes, event loop delays)
+   - Repeated failure patterns around the reported issue time
+
+5. **Extract signals from screenshots:**
+   - Visible error messages or dialogs
+   - UI freeze indicators (loading spinners stuck, unresponsive elements)
+   - Memory / resource warnings visible in UI
+
+6. **Combine user description + attachment signals** to form a diagnosis hypothesis.
+   Pass the combined evidence to Step 1.6 for triage classification.
+
+**Rate-limit note:** Same as Step 1.5 — call attachment APIs sequentially, never in parallel.
+
 #### Step 1.6: Triage — Can We Fix It?
 
 Classify each issue group using the detailed decision flow in [references/triage-rules.md](references/triage-rules.md).
 
-**Quick reference — six categories:**
+**Quick reference — seven categories:**
 
-| Category          | Action                                                   |
-| ----------------- | -------------------------------------------------------- |
-| **Direct fix**    | Stack trace → our code → fix                             |
-| **Defensive fix** | No trace, but pattern matches our code → fix with guards |
-| **Pending merge** | Open PR exists → skip or improve                         |
-| **Already fixed** | Merged PR / resolved → skip                              |
-| **System-level**  | EPIPE, ENOSPC, EIO, uv, Chromium → skip                  |
-| **Unfixable**     | No trace, no matching code → skip                        |
+| Category          | Action                                                             |
+| ----------------- | ------------------------------------------------------------------ |
+| **Direct fix**    | Stack trace → our code → fix                                       |
+| **Defensive fix** | No trace, but pattern matches our code → fix with guards           |
+| **Feedback fix**  | User feedback + attachment analysis → identifiable code path → fix |
+| **Pending merge** | Open PR exists → skip or improve                                   |
+| **Already fixed** | Merged PR / resolved → skip                                        |
+| **System-level**  | EPIPE, ENOSPC, EIO, uv, Chromium → skip                            |
+| **Unfixable**     | No trace, no matching code, no diagnostic attachments → skip       |
 
 **Output a triage report** (see [references/report-template.md](references/report-template.md) for format),
 then **proceed immediately** — do not wait for user confirmation.
@@ -455,12 +523,13 @@ re-analyzing the same issues.
 
 **TTL by classification:**
 
-| Classification    | TTL      | Reason                                            |
-| ----------------- | -------- | ------------------------------------------------- |
-| system_level      | 7 days   | These never change (EPIPE, ENOSPC, EIO, uv, etc.) |
-| already_fixed     | 48 hours | Re-check in case of regression                    |
-| unfixable         | 24 hours | Might become fixable with new code changes        |
-| fix_pending_merge | 12 hours | PR might get merged, issue might resolve          |
+| Classification    | TTL      | Reason                                                |
+| ----------------- | -------- | ----------------------------------------------------- |
+| system_level      | 7 days   | These never change (EPIPE, ENOSPC, EIO, uv, etc.)     |
+| already_fixed     | 48 hours | Re-check in case of regression                        |
+| feedback_no_clue  | 48 hours | User feedback with no diagnostic clues in attachments |
+| unfixable         | 24 hours | Might become fixable with new code changes            |
+| fix_pending_merge | 12 hours | PR might get merged, issue might resolve              |
 
 **Write rules:**
 
@@ -485,17 +554,19 @@ re-analyzing the same issues.
 
 Default parameters (can be overridden via skill args):
 
-| Parameter | Default  | Description                                                        |
-| --------- | -------- | ------------------------------------------------------------------ |
-| threshold | 100      | Minimum occurrence count (batch mode only)                         |
-| project   | electron | Sentry project slug                                                |
-| sort      | freq     | Sort order for issues                                              |
-| limit     | 0        | Max issues to fix per invocation (0 = unlimited, >0 = daemon mode) |
+| Parameter        | Default  | Description                                                        |
+| ---------------- | -------- | ------------------------------------------------------------------ |
+| threshold        | 100      | Minimum occurrence count (batch mode only)                         |
+| project          | electron | Sentry project slug                                                |
+| sort             | freq     | Sort order for issues                                              |
+| limit            | 0        | Max issues to fix per invocation (0 = unlimited, >0 = daemon mode) |
+| include_feedback | false    | Include `event.type: default` (user feedback) issues               |
 
 Override examples:
 
 - Batch mode: `/fix-sentry threshold=50 project=electron`
 - Daemon mode: `/fix-sentry limit=1 project=electron`
+- Include user feedback: `/fix-sentry include_feedback=true`
 
 ## Mandatory Rules
 
diff --git a/.claude/skills/fix-sentry/references/report-template.md b/.claude/skills/fix-sentry/references/report-template.md
@@ -16,6 +16,11 @@ Will fix — defensive (N groups):
      → Pattern: "batch-export-*.zip" matches createZip in fsBridge.ts
      → Defensive fix: ensure parent directory exists before write
 
+Will fix — feedback (N groups):
+  1. [ELECTRON-FF] User feedback description (N events)
+     → Attachment: logs.gz — stack trace found pointing to src/renderer/hooks/useChat.ts
+     → Feedback fix: add timeout guard for stalled stream response
+
 Fix pending merge (P groups):
   1. [ELECTRON-ZZ] Error description (N events)
      → PR #1234 (OPEN) — fix submitted but not yet merged/deployed
@@ -42,6 +47,13 @@ Fixed — PR Created (N groups, covering X Sentry issues):
 
   2. ...
 
+Fixed — From Feedback (F groups):
+  1. [ELECTRON-FF] User-reported UI freeze during stream response
+     PR: <pr-url>
+     Issue: #<number>
+     Diagnosis: logs.gz contained repeated ETIMEDOUT in useChat hook
+     Verification: PASS — unit tests pass
+
 Fixed — Pending Manual Review (P groups):
   1. [ELECTRON-YY] Worker process error
      PR: <pr-url> (draft)
@@ -56,5 +68,5 @@ Skipped (K issues):
   1. [ELECTRON-J] write EPIPE
      → Reason: System-level error, no application code
 
-Total: N fixed (PR created), P pending review, M already fixed, K skipped
+Total: N fixed (PR created), F from feedback, P pending review, M already fixed, K skipped
 ```
diff --git a/.claude/skills/fix-sentry/references/triage-rules.md b/.claude/skills/fix-sentry/references/triage-rules.md
@@ -56,6 +56,23 @@ patterns. If a matching code path is found, trace its error handling and apply a
 | Error is purely user-specific with no matching code     | Skip          |
 | Error references app-internal files (config, resources) | Defensive fix |
 
+## Step C2: Feedback fix — User-reported issue with diagnostic attachments
+
+Issues with `event.type: "default"` are user-submitted feedback, not automatic crash reports.
+These have no stack trace but may include attachments (logs, screenshots) with diagnostic clues.
+
+**Prerequisite:** Step 1.5b (Attachment Analysis) must have run first.
+
+| Scenario                                                             | Result                                |
+| -------------------------------------------------------------------- | ------------------------------------- |
+| Log attachment contains stack trace pointing to our code             | Promote to Direct fix (Step B)        |
+| Log attachment shows resource exhaustion (OOM, CPU 100%) in our code | Defensive fix                         |
+| Log attachment shows repeated errors matching our code paths         | Defensive fix                         |
+| Screenshot shows frozen UI with identifiable component               | Defensive fix                         |
+| User description + logs suggest a specific code path                 | Defensive fix                         |
+| Logs show only system / third-party issues                           | Skip (system-level)                   |
+| No attachments, no matching code path from description               | Skip (unfixable — needs human triage) |
+
 ## Step D: Skip filters (apply to all categories)
 
 | Condition                                  | Action                        |
@@ -66,11 +83,12 @@ patterns. If a matching code path is found, trace its error handling and apply a
 
 ## Classification Summary
 
-| Category          | Criteria                                           | Action                        |
-| ----------------- | -------------------------------------------------- | ----------------------------- |
-| **Direct fix**    | Stack trace → our code, clear cause                | Fix with targeted code change |
-| **Defensive fix** | No stack trace, but error path matches our code    | Fix with defensive guards     |
-| **Pending merge** | Existing OPEN PR addresses the root cause          | Skip or improve existing PR   |
-| **Already fixed** | Merged PR / resolved in Sentry                     | Skip                          |
-| **System-level**  | EPIPE, ENOSPC, EIO, uv, Chromium internal          | Skip                          |
-| **Unfixable**     | No stack trace, no matching code path, third-party | Skip                          |
+| Category          | Criteria                                                     | Action                        |
+| ----------------- | ------------------------------------------------------------ | ----------------------------- |
+| **Direct fix**    | Stack trace → our code, clear cause                          | Fix with targeted code change |
+| **Defensive fix** | No stack trace, but error path matches our code              | Fix with defensive guards     |
+| **Feedback fix**  | User feedback + attachment analysis → identifiable code path | Fix based on diagnostic clues |
+| **Pending merge** | Existing OPEN PR addresses the root cause                    | Skip or improve existing PR   |
+| **Already fixed** | Merged PR / resolved in Sentry                               | Skip                          |
+| **System-level**  | EPIPE, ENOSPC, EIO, uv, Chromium internal                    | Skip                          |
+| **Unfixable**     | No stack trace, no matching code path, no attachments        | Skip                          |
PATCH

echo "Gold patch applied."
