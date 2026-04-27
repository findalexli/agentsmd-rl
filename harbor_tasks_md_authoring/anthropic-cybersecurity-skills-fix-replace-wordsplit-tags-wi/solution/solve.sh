#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anthropic-cybersecurity-skills

# Idempotency guard
if grep -qF "- cloud-security" "skills/analyzing-azure-activity-logs-for-threats/SKILL.md" && grep -qF "- incident-response" "skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md" && grep -qF "- obfuscation-detection" "skills/analyzing-powershell-script-block-logging/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/analyzing-azure-activity-logs-for-threats/SKILL.md b/skills/analyzing-azure-activity-logs-for-threats/SKILL.md
@@ -8,10 +8,12 @@ description: 'Queries Azure Monitor activity logs and sign-in logs via azure-mon
 domain: cybersecurity
 subdomain: security-operations
 tags:
-- analyzing
 - azure
-- activity
-- logs
+- cloud-security
+- azure-monitor
+- kql
+- threat-hunting
+- activity-logs
 version: '1.0'
 author: mahipal
 license: Apache-2.0
diff --git a/skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md b/skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md
@@ -8,10 +8,12 @@ description: 'Performs Linux memory acquisition using LiME (Linux Memory Extract
 domain: cybersecurity
 subdomain: security-operations
 tags:
-- analyzing
-- memory
-- forensics
-- with
+- memory-forensics
+- linux-forensics
+- lime
+- volatility
+- incident-response
+- kernel-modules
 version: '1.0'
 author: mahipal
 license: Apache-2.0
diff --git a/skills/analyzing-powershell-script-block-logging/SKILL.md b/skills/analyzing-powershell-script-block-logging/SKILL.md
@@ -6,10 +6,12 @@ description: Parse Windows PowerShell Script Block Logs (Event ID 4104) from EVT
 domain: cybersecurity
 subdomain: security-operations
 tags:
-- analyzing
 - powershell
-- script
-- block
+- script-block-logging
+- event-id-4104
+- obfuscation-detection
+- windows-forensics
+- endpoint-security
 version: '1.0'
 author: mahipal
 license: Apache-2.0
PATCH

echo "Gold patch applied."
