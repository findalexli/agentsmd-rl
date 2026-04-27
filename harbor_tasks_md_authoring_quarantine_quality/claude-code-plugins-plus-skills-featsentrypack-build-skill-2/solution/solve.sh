#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "An alert fires: `PaymentProcessingError` with 200 events in 5 minutes. Triage re" "plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md b/plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md
@@ -1,205 +1,295 @@
 ---
 name: sentry-incident-runbook
 description: |
-  Incident response procedures using Sentry.
-  Use when investigating production issues, triaging errors,
-  or creating incident response workflows.
-  Trigger with phrases like "sentry incident response", "sentry triage",
-  "investigate sentry error", "sentry runbook".
-allowed-tools: Read, Write, Edit, Grep, Bash(curl:*), Bash(node:*)
+  Execute incident response procedures using Sentry error monitoring.
+  Use when investigating production outages, triaging error spikes,
+  classifying incident severity, or building postmortem reports from Sentry data.
+  Trigger with phrases like "sentry incident", "sentry triage",
+  "investigate sentry error", "sentry runbook", "production incident sentry".
+allowed-tools: Read, Write, Edit, Grep, Bash(curl:*), Bash(node:*), Bash(npx:*), Bash(python3:*)
 version: 1.0.0
 license: MIT
 author: Jeremy Longshore <jeremy@intentsolutions.io>
-compatible-with: claude-code, codex, openclaw
-tags: [saas, sentry, workflow, incident-response, triage]
-
+compatible-with: claude-code
+tags: [saas, sentry, incident-response, triage, observability]
 ---
+
 # Sentry Incident Runbook
 
+## Overview
+
+Structured incident response framework built on Sentry's error monitoring platform. Covers the full lifecycle from alert detection through severity classification, root cause investigation using Sentry's breadcrumbs and stack traces, Discover queries for impact analysis, stakeholder communication, resolution via the Sentry API, and postmortem documentation with Sentry data exports.
+
 ## Prerequisites
-- Sentry account with access to project issues
-- Alert rules configured for critical errors
-- Team notification channels set up (Slack, PagerDuty)
-- Access to Sentry API with auth token
+
+- Sentry account with project-level access and auth token (`SENTRY_AUTH_TOKEN`)
+- Organization slug (`SENTRY_ORG`) and project slug (`SENTRY_PROJECT`) configured
+- `@sentry/node` (v8+) or equivalent SDK installed in the application
+- Alert rules configured for critical error thresholds
+- Notification channels connected (Slack integration or PagerDuty)
 
 ## Instructions
 
-### 1. Severity Classification
+### Step 1 — Classify Severity
 
-| Severity | Criteria | Response Time | Escalation |
-|----------|----------|--------------|------------|
-| **P0 — Critical** | Crash-free rate < 95%, payment failures, data loss | 15 min | PagerDuty on-call |
-| **P1 — Major** | New error affecting > 100 users/hr, core feature broken | 1 hour | Slack #alerts-critical |
-| **P2 — Minor** | New error affecting < 100 users/hr, workaround exists | Same day | Slack #alerts-production |
-| **P3 — Low** | Edge case, cosmetic, staging-only | Next sprint | Backlog |
+Assign a severity level based on error frequency and user impact. This determines response time and escalation path.
 
-### 2. Initial Triage Checklist
+| Severity | Error Criteria | User Impact | Response Time | Escalation |
+|----------|---------------|-------------|---------------|------------|
+| **P0 — Critical** | Crash-free rate below 95% or unhandled exception spike >500/min | Core flow blocked for all users, data loss risk | 15 minutes | PagerDuty page to on-call engineer |
+| **P1 — Major** | New issue affecting >100 unique users per hour | Key feature degraded, no workaround | 1 hour | Slack `#incidents` channel, tag team lead |
+| **P2 — Minor** | New issue affecting <100 unique users per hour | Feature degraded but workaround exists | Same business day | Slack `#alerts-production` |
+| **P3 — Low** | Edge case, cosmetic error, staging-only issue | Minimal or no user-facing impact | Next sprint | Add to backlog, assign owner |
 
-When an alert fires:
+Decision logic for classification:
 
 ```
-[ ] 1. Open Sentry issue link from alert
-[ ] 2. Check error frequency graph — is it spiking or steady?
-[ ] 3. Check "First Seen" and "Last Seen" — is this new or recurring?
-[ ] 4. Check affected users count
-[ ] 5. Check environment — production, staging, or dev?
-[ ] 6. Check release — which deployment introduced this?
-[ ] 7. Read stack trace — identify the failing line
-[ ] 8. Check breadcrumbs — what happened before the error?
-[ ] 9. Check "Suspect Commits" — which commit likely caused it?
-[ ] 10. Classify severity and communicate status
+Alert fires →
+├── Check crash-free rate (Project Settings → Crash Free Sessions)
+│   └── Below 95%? → P0
+├── Check unique users affected (Issue Details → Users tab)
+│   ├── >100/hr on core flow? → P1
+│   └── <100/hr or workaround exists? → P2
+└── Staging-only or edge case? → P3
 ```
 
-### 3. Sentry API for Incident Investigation
+### Step 2 — Triage and Investigate
+
+Execute this checklist within the first 15 minutes of a P0/P1 alert.
+
+**Initial triage (Sentry UI):**
+
+1. Open the Sentry issue link from the alert notification
+2. Check the error frequency graph — determine if the rate is spiking, steady, or declining
+3. Read the "First Seen" and "Last Seen" timestamps to determine if this is new or a regression
+4. Check the "Users" count on the issue to quantify impact
+5. Verify the environment filter — confirm this is production, not staging
+6. Check the "Release" tag — identify which deployment introduced the error
+7. Open "Suspect Commits" to find the likely-causal changeset
+
+**Deep investigation (stack trace and breadcrumbs):**
+
+8. Read the full stack trace — identify the failing function and line number
+9. Expand the breadcrumbs panel — trace the sequence of events leading to the error (HTTP requests, console logs, navigation, UI clicks)
+10. Check the user context panel for device, browser, OS, and custom user tags
+11. Review the "Tags" panel for patterns (specific release, region, browser)
+
+**API-based investigation:**
 
 ```bash
-# Get issue details
+# Fetch issue details programmatically
 curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
   "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/" \
   | python3 -c "
 import json, sys
 issue = json.load(sys.stdin)
-print(f\"Title: {issue['title']}\")
-print(f\"First Seen: {issue['firstSeen']}\")
-print(f\"Last Seen: {issue['lastSeen']}\")
-print(f\"Events: {issue['count']}\")
-print(f\"Users: {issue['userCount']}\")
-print(f\"Level: {issue['level']}\")
-print(f\"Status: {issue['status']}\")
-"
-
-# Get latest events for the issue
+print(f'Title:      {issue[\"title\"]}')
+print(f'First Seen: {issue[\"firstSeen\"]}')
+print(f'Last Seen:  {issue[\"lastSeen\"]}')
+print(f'Events:     {issue[\"count\"]}')
+print(f'Users:      {issue[\"userCount\"]}')
+print(f'Level:      {issue[\"level\"]}')
+print(f'Status:     {issue[\"status\"]}')
+print(f'Platform:   {issue.get(\"platform\", \"unknown\")}')
+" || echo "ERROR: Failed to fetch issue — check SENTRY_AUTH_TOKEN and ISSUE_ID"
+
+# Fetch latest events for the issue (most recent 5)
 curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
   "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/events/?per_page=5" \
   | python3 -c "
 import json, sys
 events = json.load(sys.stdin)
 for e in events:
-    print(f\"Event: {e['eventID']} | {e.get('dateCreated', 'N/A')} | Release: {e.get('release', {}).get('version', 'N/A')}\")
-"
-```
-
-### 4. Error Pattern Identification
-
-Common patterns and their likely causes:
-
-**Deployment-related (error starts at deploy time):**
-```
-Diagnostic: Check "First Seen" time vs. latest deploy time
-Fix: Rollback to previous release
-  sentry-cli releases deploys "$PREVIOUS_VERSION" new --env production
-```
-
-**Third-party failure (external service errors):**
-```
-Diagnostic: Check error message for external hostnames
-Check: Breadcrumbs showing failed HTTP calls
-Fix: Enable circuit breaker, add retry logic, alert on dependency health
+    release = e.get('release', {})
+    ver = release.get('version', 'N/A') if isinstance(release, dict) else 'N/A'
+    print(f'Event {e[\"eventID\"][:12]} | {e.get(\"dateCreated\", \"N/A\")} | Release: {ver}')
+" || echo "ERROR: Failed to fetch events"
 ```
 
-**Data corruption (validation/parsing errors):**
-```
-Diagnostic: Check event context for malformed data samples
-Fix: Add input validation, fix data pipeline, backfill corrupted records
-```
+**Sentry Discover queries for impact analysis:**
 
-**Resource exhaustion (OOM, connection pool, timeouts):**
-```
-Diagnostic: Check error rate correlation with traffic
-Fix: Scale resources, add connection pooling, implement rate limiting
+```bash
+# Count total events and unique affected users in last 24 hours
+curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
+  "https://sentry.io/api/0/organizations/$SENTRY_ORG/events/" \
+  --data-urlencode "field=count()" \
+  --data-urlencode "field=count_unique(user)" \
+  --data-urlencode "query=issue.id:$ISSUE_ID" \
+  --data-urlencode "statsPeriod=24h" \
+  -G | python3 -c "
+import json, sys
+data = json.load(sys.stdin)
+if 'data' in data and data['data']:
+    row = data['data'][0]
+    print(f'Events (24h):       {row.get(\"count()\", \"N/A\")}')
+    print(f'Unique users (24h): {row.get(\"count_unique(user)\", \"N/A\")}')
+" || echo "ERROR: Discover query failed"
+
+# Check p95 transaction duration for affected endpoint
+curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
+  "https://sentry.io/api/0/organizations/$SENTRY_ORG/events/" \
+  --data-urlencode "field=transaction" \
+  --data-urlencode "field=p95(transaction.duration)" \
+  --data-urlencode "field=count()" \
+  --data-urlencode "query=has:transaction event.type:transaction" \
+  --data-urlencode "statsPeriod=1h" \
+  --data-urlencode "sort=-count()" \
+  --data-urlencode "per_page=5" \
+  -G | python3 -c "
+import json, sys
+data = json.load(sys.stdin)
+if 'data' in data:
+    for row in data['data']:
+        txn = row.get('transaction', 'unknown')
+        p95 = row.get('p95(transaction.duration)', 0)
+        cnt = row.get('count()', 0)
+        print(f'{txn}: p95={p95:.0f}ms, count={cnt}')
+" || echo "ERROR: Transaction query failed"
 ```
 
-### 5. Incident Communication Templates
-
-**Initial Alert (within 15 min of P0):**
-```
-:rotating_light: INCIDENT — [Service Name]
-Status: Investigating
-Impact: [What users are experiencing]
-Started: [Timestamp]
-Sentry: [Link to issue]
-Lead: @[on-call engineer]
-Next update: 30 minutes
-```
+### Step 3 — Resolve, Communicate, and Document
 
-**Status Update (every 30 min for P0):**
-```
-UPDATE — [Service Name] Incident
-Status: [Investigating | Identified | Monitoring | Resolved]
-Root cause: [Brief description or "still investigating"]
-Actions taken: [What's been done]
-Next steps: [What's planned]
-ETA: [When we expect resolution]
-```
+**Identify the root cause pattern:**
 
-**Resolution:**
-```
-:white_check_mark: RESOLVED — [Service Name]
-Duration: [X hours Y minutes]
-Root cause: [What caused it]
-Fix: [What was done]
-Postmortem: [Link — due within 48 hours]
-```
+| Pattern | Diagnostic Signal | Immediate Action |
+|---------|------------------|-----------------|
+| Deployment regression | "First Seen" aligns with latest deploy timestamp | Rollback via `sentry-cli releases deploys $PREV_VERSION new --env production` |
+| Third-party failure | Breadcrumbs show failed HTTP calls to external hosts | Enable circuit breaker, add retry logic, monitor dependency status |
+| Data corruption | Event context contains malformed input samples | Add input validation, fix data pipeline upstream |
+| Resource exhaustion | Error rate correlates with traffic spikes (OOM, pool exhaustion) | Scale horizontally, add connection pooling, implement rate limiting |
+| SDK misconfiguration | Events missing context, breadcrumbs, or release info | Review `Sentry.init()` options, verify source maps uploaded |
 
-### 6. Resolving Issues in Sentry
+**Resolve the issue via Sentry API:**
 
 ```bash
-# Mark issue as resolved
-curl -X PUT \
+# Mark issue as resolved (closes the issue)
+curl -s -X PUT \
   -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"status": "resolved"}' \
-  "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/"
+  "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/" \
+  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Status: {d.get(\"status\",\"unknown\")}')" \
+  || echo "ERROR: Failed to resolve issue"
 
-# Resolve in next release (auto-reopens if it regresses)
-curl -X PUT \
+# Resolve in next release (auto-reopens on regression)
+curl -s -X PUT \
   -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"status": "resolved", "statusDetails": {"inNextRelease": true}}' \
-  "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/"
+  "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/" \
+  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Status: {d.get(\"status\",\"unknown\")} (regression detection enabled)')" \
+  || echo "ERROR: Failed to resolve issue"
 
-# Ignore issue (snooze — won't alert again)
-curl -X PUT \
+# Ignore with threshold (snooze until count exceeds limit)
+# Use 100 as the re-alert threshold for noisy low-severity issues
+curl -s -X PUT \
   -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"status": "ignored", "statusDetails": {"ignoreCount": 100}}' \
-  "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/"
+  "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/$ISSUE_ID/" \
+  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Status: {d.get(\"status\",\"unknown\")} (snoozed until 100 events)')" \
+  || echo "ERROR: Failed to ignore issue"
 ```
 
-### 7. Postmortem Checklist
+**Stakeholder communication templates:**
+
+Initial alert (send within 15 minutes of P0):
+
+```
+INCIDENT — [Service Name]
+Status: Investigating
+Impact: [Description of user-facing symptoms]
+Started: [Timestamp from Sentry "First Seen"]
+Sentry Issue: [Link to issue]
+Incident Lead: @[on-call engineer]
+Next update: 30 minutes
+```
 
-After resolution, complete within 48 hours:
+Resolution notice:
 
 ```
-[ ] Timeline of events (when detected, when mitigated, when resolved)
-[ ] Root cause analysis (5 Whys)
-[ ] Impact assessment (users affected, duration, revenue impact)
-[ ] What went well (detection, response, communication)
-[ ] What could improve (monitoring gaps, process issues)
-[ ] Action items with owners and deadlines
-[ ] Sentry configuration changes (new alerts, better grouping)
-[ ] Prevention measures (tests, validation, monitoring)
+RESOLVED — [Service Name]
+Duration: [Total incident time from first alert to resolution]
+Root Cause: [One-line description from investigation]
+Fix Applied: [What changed — rollback, hotfix, config change]
+Postmortem: [Link — due within 48 hours]
+```
+
+**Postmortem template with Sentry data:**
+
+```markdown
+## Incident Postmortem: [Title from Sentry Issue]
+
+### Timeline
+- [HH:MM] Alert fired — Sentry issue [ISSUE_ID] created
+- [HH:MM] On-call engineer acknowledged
+- [HH:MM] Root cause identified via [breadcrumbs / stack trace / suspect commits]
+- [HH:MM] Fix deployed — [rollback / hotfix description]
+- [HH:MM] Error rate returned to baseline, issue resolved in Sentry
+
+### Impact (from Sentry Discover)
+- **Duration:** [X hours Y minutes]
+- **Total events:** [count() from Discover query]
+- **Unique users affected:** [count_unique(user) from Discover query]
+- **p95 latency during incident:** [p95(transaction.duration) from Discover]
+
+### Root Cause (5 Whys)
+1. Why did the error occur? [Direct cause from stack trace]
+2. Why was that code path triggered? [From breadcrumbs]
+3. Why was it not caught in testing? [Gap analysis]
+4. Why did the alert take [X] minutes? [Alert rule review]
+5. Why is this class of error possible? [Systemic cause]
+
+### Action Items
+- [ ] [Preventive measure] — Owner: @[name] — Due: [date]
+- [ ] Update Sentry alert rules to catch [pattern] earlier
+- [ ] Add regression test covering [scenario from breadcrumbs]
+- [ ] Review and tighten ownership rules for [component]
 ```
 
 ## Output
-- Severity classification framework (P0-P3)
-- Triage checklist for rapid incident assessment
-- API commands for investigating issues programmatically
-- Communication templates for stakeholder updates
-- Issue resolution via API (resolve, ignore, snooze)
-- Postmortem checklist for continuous improvement
+
+- Severity classification (P0-P3) based on error frequency and user impact
+- Completed triage checklist with root cause identification
+- Sentry Discover query results quantifying incident impact
+- API-driven issue resolution with regression detection enabled
+- Stakeholder communication messages (initial alert + resolution)
+- Postmortem document populated with Sentry data exports
 
 ## Error Handling
 
 | Error | Cause | Solution |
 |-------|-------|----------|
-| Alert fatigue | Too many P2/P3 alerts | Tune alert thresholds, use "New issue" not "Every event" |
-| Can't find root cause | Missing context in events | Add breadcrumbs, tags, and user context to SDK config |
-| Issue keeps regressing | Resolved in current release but root cause not fixed | Use "Resolve in next release" to detect regressions |
-| Suspect commits wrong | Commit association not configured | Set up `sentry-cli releases set-commits --auto` |
+| `401 Unauthorized` from Sentry API | Auth token expired or lacks org-level scope | Regenerate token at Settings > Developer Settings > Internal Integrations with `event:read`, `issue:write` scopes |
+| Alert fatigue — too many P2/P3 alerts | Alert rules trigger on every event instead of thresholds | Change alert condition to "New issue" or "Event frequency > N in M minutes" |
+| Suspect Commits shows wrong commit | Release association not configured | Run `sentry-cli releases set-commits --auto` in CI pipeline |
+| Missing breadcrumbs in events | SDK not capturing HTTP/console/navigation breadcrumbs | Verify `Sentry.init({ integrations: [breadcrumbsIntegration()] })` and check `maxBreadcrumbs` setting |
+| Issue keeps regressing after resolve | Root cause not fully addressed, only symptom fixed | Use "Resolve in next release" for auto-reopen, add regression test |
+| Discover query returns empty data | Wrong time range or missing `event.type` filter | Expand `statsPeriod` to `7d`, verify query syntax in Sentry Discover UI first |
+
+## Examples
+
+**Example 1 — P0 payment failure spike:**
+
+An alert fires: `PaymentProcessingError` with 200 events in 5 minutes. Triage reveals crash-free rate dropped to 91%. Breadcrumbs show the Stripe webhook handler receiving malformed payloads after a Stripe API version change. Suspect Commits points to a dependency update merged 20 minutes ago. Resolution: rollback the deployment, resolve the Sentry issue with `inNextRelease`, file a postmortem with the 5 Whys showing the missing Stripe API version pin.
+
+**Example 2 — P2 intermittent 503 from upstream API:**
+
+Sentry shows `ServiceUnavailableError` affecting 40 users/hour. Discover query reveals `count()` = 180, `count_unique(user)` = 40, `p95(transaction.duration)` = 8200ms. Breadcrumbs show the third-party geocoding API returning 503. Resolution: enable the circuit breaker fallback to cached results, ignore the Sentry issue with `ignoreCount: 100`, create a backlog item to add a secondary geocoding provider.
+
+**Example 3 — P1 new unhandled exception after deploy:**
+
+A `TypeError: Cannot read properties of undefined` appears immediately after a release tagged `v2.4.1`. First Seen matches the deploy timestamp. Stack trace points to a renamed API response field. Suspect Commits identifies the exact PR. Resolution: deploy hotfix renaming the field access, resolve the issue tied to `v2.4.2`, update the postmortem with Discover data showing 320 affected users over 45 minutes.
 
 ## Resources
-- [Issue Details](https://docs.sentry.io/product/issues/issue-details/)
-- [Alerts](https://docs.sentry.io/product/alerts/)
-- [Issues API](https://docs.sentry.io/api/events/)
-- [Ownership Rules](https://docs.sentry.io/product/issues/ownership-rules/)
+
+- [Sentry Issue Details](https://docs.sentry.io/product/issues/issue-details/) — anatomy of an issue page
+- [Sentry Alerts](https://docs.sentry.io/product/alerts/) — configuring alert rules and thresholds
+- [Sentry Discover Queries](https://docs.sentry.io/product/explore/discover-queries/) — building impact analysis queries
+- [Issues API](https://docs.sentry.io/api/events/list-a-projects-issues/) — programmatic issue management
+- [Ownership Rules](https://docs.sentry.io/product/issues/ownership-rules/) — auto-assigning issues to teams
+- [`@sentry/node` SDK](https://docs.sentry.io/platforms/javascript/guides/node/) — Node.js SDK configuration
+
+## Next Steps
+
+For configuring Sentry alerts and error capture, see `sentry-error-capture`. For CI/CD integration with Sentry releases, see `sentry-ci-integration`. For performance monitoring and tracing, see `sentry-performance-tracing`.
PATCH

echo "Gold patch applied."
