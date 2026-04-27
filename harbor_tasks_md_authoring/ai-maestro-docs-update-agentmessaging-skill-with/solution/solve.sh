#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-maestro

# Idempotency guard
if grep -qF "- If still not found, the error shows available hosts - check those for valid ag" "skills/agent-messaging/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/agent-messaging/SKILL.md b/skills/agent-messaging/SKILL.md
@@ -298,24 +298,43 @@ send-aimaestro-message.sh <to_agent[@host]> <subject> <message> [priority] [type
 ```
 
 **Parameters:**
-- `to_agent[@host]` (required) - Target agent with optional host:
-  - `backend-api` - Send to agent on same host (auto-detected)
-  - `backend-api@mac-mini` - Send to agent on remote host "mac-mini"
-  - `backend-api@macbook-pro` - Explicitly specify the host by hostname
+- `to_agent[@host]` (required) - Target agent (host is optional thanks to smart lookup):
+  - `backend-api` - Script automatically searches ALL hosts to find this agent
+  - `api-form` - Fuzzy matching: finds `api-forms` even with typos/partial names
+  - `backend-api@mac-mini` - Explicitly specify host (skips search, faster)
 - `subject` (required) - Brief subject line
 - `message` (required) - Message content to send TO OTHER AGENT
 - `priority` (optional) - low | normal | high | urgent (default: normal)
+
+**Smart Lookup (v0.17.32+):**
+When no `@host` is specified, the script automatically:
+1. Searches ALL enabled hosts for the agent
+2. If found on exactly 1 host → sends automatically
+3. If found on multiple hosts → asks which one you meant
+4. If not found → tries fuzzy/partial matching
+
+**Fuzzy Matching (v0.17.33+):**
+If exact name not found, searches for partial matches:
+- `api-form` → finds `api-forms` (typo tolerance)
+- `forms` → finds `23blocks-api-forms` (partial name)
+- Single fuzzy match: shows `🔍 Found partial match: ...` then sends
+- Multiple fuzzy matches: shows options for clarification
 - `type` (optional) - request | response | notification | update (default: request)
 
 **Examples:**
 ```bash
-# Simple request (local agent)
+# Simple request - smart lookup finds agent automatically
 send-aimaestro-message.sh backend-architect "Need API endpoint" "Please implement POST /api/users with pagination"
 
-# Cross-host message (agent on remote machine)
+# Works with partial names - fuzzy matching finds the right agent
+send-aimaestro-message.sh api-form "Customer data sync" "Please sync customer records"
+# Output: 🔍 Found partial match: api-forms@hostname
+# ✅ Message sent
+
+# Explicit host (faster - skips search)
 send-aimaestro-message.sh crm-api@mac-mini "Customer data sync" "Please sync customer records from CRM" high request
 
-# Urgent notification (local)
+# Urgent notification
 send-aimaestro-message.sh frontend-dev "Production issue" "API returning 500 errors" urgent notification
 
 # Response to request
@@ -374,11 +393,17 @@ send-aimaestro-message.sh data-processor@cloud-server "Process batch" "Run night
 
 ### How Cross-Host Messaging Works
 
-1. **Parse destination**: Script parses `agent@host` format
-2. **Resolve host URL**: Looks up host URL from `~/.aimaestro/hosts.json`
-3. **Resolve agent**: Queries remote host's API to verify agent exists
-4. **Send directly**: POST message to remote host's `/api/messages` endpoint
-5. **Local copy**: Saves copy in sender's sent folder
+**With explicit host (`agent@host`):**
+1. Parse destination and look up host URL from `~/.aimaestro/hosts.json`
+2. Query that specific host's API to resolve agent
+3. Send message to that host's `/api/messages` endpoint
+
+**Without host (smart lookup):**
+1. Search ALL enabled hosts for the agent (exact match first)
+2. If not found exactly, try fuzzy/partial matching on all hosts
+3. Single match → auto-select that host and send
+4. Multiple matches → prompt for clarification
+5. No matches → show helpful error with available hosts
 
 ### Message Display with Hosts
 
@@ -698,8 +723,11 @@ send-aimaestro-message.sh frontend-dev \
 - Check PATH: `which send-aimaestro-message.sh`
 
 **Agent not found:**
-- Agent names are aliases or IDs from the agent registry
-- Use the agents API to see valid agent names on each host
+- The script automatically searches all hosts and tries fuzzy matching
+- If still not found, the error shows available hosts - check those for valid agent names
+- Use `list-agents.sh` to see all agents on local host
+- Use `list-agents.sh <host-id>` to see agents on a specific remote host
+- Try partial names - fuzzy matching handles typos and abbreviations
 
 ## References
 
PATCH

echo "Gold patch applied."
