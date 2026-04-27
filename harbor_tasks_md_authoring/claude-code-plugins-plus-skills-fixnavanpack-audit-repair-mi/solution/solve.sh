#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md" "plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md" && grep -qF "plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md" "plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md" && grep -qF "plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md" "plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md" && grep -qF "| Missing env vars | N/A | Config loader throws on startup; check the correct `." "plugins/saas-packs/navan-pack/skills/navan-multi-env-setup/SKILL.md" && grep -qF "plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md" "plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md" && grep -qF "plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md" "plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md" && grep -qF "plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md" "plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md
@@ -13,6 +13,8 @@ compatible-with: claude-code
 
 # Navan Debug Bundle
 
+## Overview
+
 Collect diagnostic data from Navan REST API integrations into a structured, shareable debug bundle. Navan has no SDK — all debugging uses raw HTTP requests against their OAuth 2.0 REST endpoints.
 
 ## Prerequisites
@@ -99,7 +101,7 @@ tar -czf "${BUNDLE_DIR}.tar.gz" "$BUNDLE_DIR"
 echo "Debug bundle ready: ${BUNDLE_DIR}.tar.gz ($(du -h "${BUNDLE_DIR}.tar.gz" | cut -f1))"
 ```
 
-## Expected Output
+## Output
 
 A compressed tarball containing:
 
diff --git a/plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md
@@ -13,6 +13,8 @@ compatible-with: claude-code
 
 # Navan Incident Runbook
 
+## Overview
+
 Structured incident response for Navan travel platform disruptions. Navan uses raw REST APIs with OAuth 2.0 — there is no SDK and no sandbox. All diagnostic commands run against production.
 
 ## Prerequisites
@@ -117,7 +119,7 @@ cat > "incident-$(date +%Y%m%d-%H%M%S).md" <<'INCEOF'
 INCEOF
 ```
 
-## Expected Output
+## Output
 
 - Severity classification for the incident
 - API health check results confirming platform vs local issue
diff --git a/plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md
@@ -13,6 +13,8 @@ compatible-with: claude-code
 
 # Navan Migration Deep Dive
 
+## Overview
+
 End-to-end migration playbook for moving from SAP Concur or legacy travel management systems to Navan. Navan uses REST APIs with OAuth 2.0 — there is no SDK, no automated migration tool, and no sandbox for testing.
 
 ## Prerequisites
@@ -141,7 +143,7 @@ curl -s -H "Authorization: Bearer $TOKEN" \
 - Maintain source system in read-only mode for 90 days (historical reference)
 - Decommission source system after retention period
 
-## Expected Output
+## Output
 
 - Migration project plan with phase timelines and owners
 - Data mapping document (source fields to Navan structure)
diff --git a/plugins/saas-packs/navan-pack/skills/navan-multi-env-setup/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-multi-env-setup/SKILL.md
@@ -258,11 +258,11 @@ A complete environment isolation strategy for Navan integrations: separate OAuth
 ## Error Handling
 | Error | Code | Solution |
 |-------|------|----------|
-| Missing env vars | N/A | Config loader throws on startup; check the correct `.env.{env}` file exists |
+| Missing env vars | N/A | Config loader throws on startup; check the correct `.env.<environment>` file exists |
 | Write blocked in read-only | 403 | Expected in dev mode; switch to staging/prod for write operations |
 | Mock endpoint not found | 501 | Add the endpoint to mock server; check test expectations match mock data |
 | Proxy connection refused | 502 | Ensure the proxy server is running; check port availability |
-| Wrong environment loaded | N/A | Verify NODE_ENV matches the intended `.env.{env}` file |
+| Wrong environment loaded | N/A | Verify NODE_ENV matches the intended `.env.<environment>` file |
 
 ## Examples
 
diff --git a/plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md
@@ -13,6 +13,8 @@ compatible-with: claude-code
 
 # Navan Production Checklist
 
+## Overview
+
 Gated production readiness verification for Navan REST API integrations. Navan has no SDK and no sandbox — production is the only environment, making this checklist critical.
 
 ## Prerequisites
@@ -112,7 +114,7 @@ curl -s -H "Authorization: Bearer $TOKEN" \
 - [ ] **Data classification**: Navan data (PII, payment info) classified and handled per PCI DSS L1
 - [ ] **Compliance certifications verified**: Confirm Navan's SOC 1/2 Type II, ISO 27001, PCI DSS L1, GDPR status at [navan.com/security](https://navan.com/security)
 
-## Expected Output
+## Output
 
 A completed checklist with:
 - Pass/fail status for each domain
diff --git a/plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md
@@ -13,6 +13,8 @@ compatible-with: claude-code
 
 # Navan Reference Architecture
 
+## Overview
+
 Production-grade architecture for Navan API integrations. Navan provides raw REST endpoints with OAuth 2.0 — no SDK, no webhooks, no sandbox. This architecture handles those constraints with five purpose-built layers.
 
 ## Prerequisites
@@ -152,7 +154,7 @@ Navan has no push/webhook mechanism — all data sync is poll-based.
 | Data sync staleness | BOOKING > 8 days old | Slack |
 | Rate limit proximity | > 80% utilization | Slack |
 
-## Expected Output
+## Output
 
 - Architecture diagram adapted to your cloud provider and tooling
 - Component specifications for each of the five layers
diff --git a/plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md b/plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md
@@ -13,6 +13,8 @@ compatible-with: claude-code
 
 # Navan Upgrade Migration
 
+## Overview
+
 Defensive patterns for maintaining Navan API integrations over time. Navan does not publicly version their API, publish a changelog, or guarantee backward compatibility. Every API response should be treated as potentially different from the last.
 
 ## Prerequisites
@@ -196,7 +198,7 @@ When a schema change is detected:
 | Endpoint URL changed | Critical | Update client config, monitor old URL for redirect |
 | Auth flow changed | Critical | Immediate attention — test `/authenticate` and `/reauthenticate` |
 
-## Expected Output
+## Output
 
 - Baseline schema snapshots stored in version control
 - Drift detection script running on a schedule (cron or CI)
PATCH

echo "Gold patch applied."
