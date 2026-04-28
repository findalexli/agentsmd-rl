#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pup

# Idempotency guard
if grep -qF "pup monitors list --tags=\"env:production\" --output=table" "skills/dd-code-generation/SKILL.md" && grep -qF "pup logs search --query=\"*\" --from=\"1h\" | jq 'group_by(.service) | map({service:" "skills/dd-logs/SKILL.md" && grep -qF "pup monitors list | jq 'sort_by(.overall_state_modified) | .[:10] | .[] | {id, n" "skills/dd-monitors/SKILL.md" && grep -qF "| Security signals | `pup security signals list --query \"*\" --from 24h` |" "skills/dd-pup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dd-code-generation/SKILL.md b/skills/dd-code-generation/SKILL.md
@@ -45,7 +45,7 @@ pup <domain> <action> [options]
 pup <domain> <subgroup> <action> [options]
 
 # Examples
-pup monitors list --tag="env:prod"
+pup monitors list --tags="env:prod"
 pup logs search --query="status:error" --from="1h"
 pup metrics query --query="avg:system.cpu.user{*}" --from="1h"
 ```
@@ -107,7 +107,7 @@ pup metrics query --query="avg:system.cpu.user{*}" --from="1h" --to="now"
 pup logs search --query="status:error service:api" --from="30m"
 
 # List monitors
-pup monitors list --tag="team:backend"
+pup monitors list --tags="team:backend"
 
 # Get dashboard
 pup dashboards get abc-123-def
@@ -492,7 +492,7 @@ pup logs search --query="status:error" --from="1h"
 **Response**:
 ```bash
 # Using pup CLI
-pup monitors list --tag="env:production" --output=table
+pup monitors list --tags="env:production" --output=table
 
 # Or generate code for your application (specify language: typescript, python, java, go, rust)
 ```
diff --git a/skills/dd-logs/SKILL.md b/skills/dd-logs/SKILL.md
@@ -37,8 +37,8 @@ pup logs search --query="status:error" --from="1h"
 # With filters
 pup logs search --query="service:api status:error" --from="1h" --limit 100
 
-# JSON output
-pup logs search --query="@http.status_code:>=500" --from="1h" --json
+# JSON output is the default
+pup logs search --query="@http.status_code:>=500" --from="1h"
 ```
 
 ### Search Syntax
@@ -58,10 +58,10 @@ Process logs before indexing:
 
 ```bash
 # List pipelines
-pup logs pipelines list
+pup obs-pipelines list
 
 # Create pipeline (JSON)
-pup logs pipelines create --json @pipeline.json
+pup obs-pipelines create --file pipeline.json
 ```
 
 ### Common Processors
@@ -108,7 +108,7 @@ pup logs pipelines create --json @pipeline.json
 
 ```bash
 # Find noisiest log sources
-pup logs search --query="*" --from="1h" --json | jq 'group_by(.service) | map({service: .[0].service, count: length}) | sort_by(-.count)[:10]'
+pup logs search --query="*" --from="1h" | jq 'group_by(.service) | map({service: .[0].service, count: length}) | sort_by(-.count)[:10]'
 ```
 
 | Exclude | Query |
@@ -139,27 +139,13 @@ pup logs archives list
 }
 ```
 
-### Rehydrate (Restore)
-
-```bash
-# Rehydrate archived logs
-pup logs rehydrate create \
-  --archive-id abc123 \
-  --from "2024-01-01T00:00:00Z" \
-  --to "2024-01-02T00:00:00Z" \
-  --query "service:api status:error"
-```
-
 ## Log-Based Metrics
 
-Create metrics from logs (cheaper than indexing):
+Inspect log-based metrics:
 
 ```bash
-# Count errors per service
-pup logs metrics create \
-  --name "api.errors.count" \
-  --query "service:api status:error" \
-  --group-by "endpoint"
+# List existing log-based metrics
+pup logs metrics list
 ```
 
 **⚠️ Cardinality warning:** Group by bounded values only.
diff --git a/skills/dd-monitors/SKILL.md b/skills/dd-monitors/SKILL.md
@@ -35,36 +35,32 @@ pup auth login
 ```bash
 pup monitors list
 pup monitors list --tags "team:platform"
-pup monitors list --status "Alert"
+pup monitors search --query "status:Alert"
 ```
 
 ### Get Monitor
 
 ```bash
-pup monitors get <id> --json
+pup monitors get <id>
 ```
 
 ### Create Monitor
 
 ```bash
-pup monitors create \
-  --name "High CPU on web servers" \
-  --type "metric alert" \
-  --query "avg(last_5m):avg:system.cpu.user{env:prod} > 80" \
-  --message "CPU above 80% @slack-ops"
+pup monitors create --file monitor.json
 ```
 
 ### Mute/Unmute
 
 ```bash
 # Mute with duration
-pup monitors mute --id 12345 --duration 1h
+pup monitors update 12345 --file monitor-muted.json
 
 # Or mute with specific end time
-pup monitors mute --id 12345 --end "2024-01-15T18:00:00Z"
+pup monitors update 12345 --file monitor-muted-until.json
 
 # Unmute
-pup monitors unmute --id 12345
+pup monitors update 12345 --file monitor-unmuted.json
 ```
 
 ## ⚠️ Monitor Creation Best Practices
@@ -167,10 +163,10 @@ def safe_mark_monitor_for_deletion(monitor_id: str, client) -> bool:
 
 ```bash
 # Find monitors without owners
-pup monitors list --json | jq '.[] | select(.tags | contains(["team:"]) | not) | {id, name}'
+pup monitors list | jq '.[] | select(.tags | contains(["team:"]) | not) | {id, name}'
 
 # Find noisy monitors (high alert count)
-pup monitors list --json | jq 'sort_by(.overall_state_modified) | .[:10] | .[] | {id, name, status: .overall_state}'
+pup monitors list | jq 'sort_by(.overall_state_modified) | .[:10] | .[] | {id, name, status: .overall_state}'
 ```
 
 ## Downtime vs Muting
@@ -182,11 +178,7 @@ pup monitors list --json | jq 'sort_by(.overall_state_modified) | .[:10] | .[] |
 
 ```bash
 # Downtime (preferred)
-pup downtime create \
-  --scope "env:prod" \
-  --monitor-tags "team:platform" \
-  --start "2024-01-15T02:00:00Z" \
-  --end "2024-01-15T06:00:00Z"
+pup downtime create --file downtime.json
 ```
 
 ## Failure Handling
diff --git a/skills/dd-pup/SKILL.md b/skills/dd-pup/SKILL.md
@@ -26,7 +26,7 @@ Pup CLI for Datadog API operations. Supports OAuth2 and API key auth.
 | List hosts | `pup infrastructure hosts list` |
 | Check SLOs | `pup slos list` |
 | On-call teams | `pup on-call teams list` |
-| Security signals | `pup security signals list --from 24h` |
+| Security signals | `pup security signals list --query "*" --from 24h` |
 | Inspect runtime values | `pup debugger probes create --service my-svc --env prod --probe-location com.example.MyClass:myMethod` |
 | Find probe-able methods | `pup symdb search --service my-svc --query MyController --view probe-locations` |
 | Check auth | `pup auth status` |
@@ -155,7 +155,7 @@ pup downtime cancel abc-123-def
 ```bash
 pup infrastructure hosts list
 pup infrastructure hosts list --filter "env:prod"
-pup infrastructure hosts list --count
+pup infrastructure hosts list --count 100
 pup infrastructure hosts get <host-id>
 ```
 
@@ -177,7 +177,7 @@ pup on-call teams get <team-id>
 
 ### Security
 ```bash
-pup security signals list --from 24h
+pup security signals list --query "*" --from 24h
 pup security signals list --query "severity:critical" --from 24h
 pup security rules list
 ```
PATCH

echo "Gold patch applied."
