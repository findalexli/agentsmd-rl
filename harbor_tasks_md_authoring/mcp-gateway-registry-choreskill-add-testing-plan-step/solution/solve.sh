#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcp-gateway-registry

# Idempotency guard
if grep -qF "description: \"Design and document new features with GitHub issue, low-level desi" ".claude/skills/new-feature-design/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/new-feature-design/SKILL.md b/.claude/skills/new-feature-design/SKILL.md
@@ -1,10 +1,10 @@
 ---
 name: new-feature-design
-description: "Design and document new features with GitHub issue, low-level design (LLD), and expert review. Creates structured documentation in .scratchpad/ with issue spec, technical design with diagrams and pseudo-code, and multi-persona expert review. Supports starting from a user description OR an existing GitHub issue URL. Folder naming: issue-{number}/ for existing issues, {feature-name}/ for new features."
+description: "Design and document new features with GitHub issue, low-level design (LLD), expert review, and testing plan. Creates structured documentation in .scratchpad/ with issue spec, technical design with diagrams and pseudo-code, multi-persona expert review, and a testing plan covering functional (curl and registry_management.py), backwards-compatibility, UX, ECS/terraform, and E2E API tests. Supports starting from a user description OR an existing GitHub issue URL. Folder naming: issue-{number}/ for existing issues, {feature-name}/ for new features."
 license: Apache-2.0
 metadata:
   author: mcp-gateway-registry
-  version: "1.4"
+  version: "1.5"
 ---
 
 # New Feature Design Skill
@@ -34,7 +34,8 @@ When the user invokes this skill:
 5. **Deep Codebase Analysis** - Thoroughly explore relevant code
 6. **Write Low-Level Design** - Create `lld.md` with technical details
 7. **Expert Review** - Create `review.md` with multi-persona feedback
-8. **Present Summary & Seek Guidance** - Present findings and ask for direction
+8. **Write Testing Plan** - Create `testing.md` with functional, backwards-compat, UX, ECS, and E2E tests
+9. **Present Summary & Seek Guidance** - Present findings and ask for direction
 
 ### GitHub Issue URL Mode Workflow
 1. **Fetch GitHub Issue** - Retrieve issue content using `gh` CLI
@@ -46,7 +47,8 @@ When the user invokes this skill:
 7. **Deep Codebase Analysis** - Thoroughly explore relevant code
 8. **Write Low-Level Design** - Create `lld.md` with technical details
 9. **Expert Review** - Create `review.md` with multi-persona feedback
-10. **Present Summary & Seek Guidance** - Present findings and ask for direction
+10. **Write Testing Plan** - Create `testing.md` with functional, backwards-compat, UX, ECS, and E2E tests
+11. **Present Summary & Seek Guidance** - Present findings and ask for direction
 
 ---
 
@@ -247,7 +249,8 @@ Create the folder structure:
 
 ├── github-issue.md    # GitHub issue specification or summary
 ├── lld.md             # Low-level design document
-└── review.md          # Expert review document
+├── review.md          # Expert review document
+└── testing.md         # Testing plan (functional, backwards-compat, UX, ECS, E2E)
 ```
 
 ## Step 4: Write GitHub Issue (github-issue.md)
@@ -1211,7 +1214,14 @@ User: "Design a new feature for rate limiting on tool calls"
    - SRE: Redis availability, monitoring needs
    - Security: Rate limit bypass prevention
    - SMTS: Overall architecture fit
-8. Present summary and seek guidance on recommendations
+8. Write `testing.md` with:
+   - Functional curl tests for the rate limit headers endpoint
+   - `registry_management.py` tests for any new CLI flags
+   - Backwards-compat tests confirming existing endpoints still respond identically when under limit
+   - UX tests for surfacing rate limit feedback in the UI
+   - ECS/terraform tests for any new env vars (e.g. `RATE_LIMIT_REDIS_URL`)
+   - E2E test exercising multiple requests to trigger and recover from a rate-limited state
+9. Present summary and seek guidance on recommendations
 
 ### Example 2: GitHub Issue URL Mode
 
@@ -1235,12 +1245,379 @@ User: "https://github.com/agentic-community/mcp-gateway-registry/issues/456"
    - Clarifications from user
    - Technical details for implementation
 9. Write `review.md` with expert feedback
-10. Present summary noting:
+10. Write `testing.md` with:
+    - Functional curl tests for new sync endpoints and existing endpoints that now honor sync state
+    - `registry_management.py` tests for any new sync-related CLI commands
+    - Backwards-compat tests confirming non-federated deployments are unaffected
+    - UX tests for any UI indicators showing federated/synced resources
+    - ECS/terraform tests for new sync config vars (e.g. `FEDERATION_PEER_URLS`, `FEDERATION_SYNC_INTERVAL_SECONDS`)
+    - E2E test exercising a two-registry sync cycle and conflict resolution
+11. Present summary noting:
     - What came from the original issue
     - What was clarified during design
     - Recommendations for implementation
 
-## Step 8: Present Summary & Seek Guidance
+## Step 8: Write Testing Plan (testing.md)
+
+Create a comprehensive testing plan document that captures **executable, copy-pasteable tests** covering every externally observable change introduced by the feature. The goal is for a reviewer or implementer to be able to walk through this document and verify the feature works end-to-end without having to invent test cases.
+
+### When Each Test Category Applies
+
+Include a category only when it is relevant to the feature. Mark a category "Not Applicable" with a short justification when it does not apply.
+
+| Category | Include When |
+|----------|--------------|
+| Functional Tests (curl) | Feature adds/modifies any HTTP endpoint |
+| Functional Tests (registry_management.py) | Feature adds/modifies anything exposed via the management CLI |
+| Backwards Compatibility Tests | Feature changes an existing endpoint, schema, CLI command, config default, or data model |
+| UX Tests | Feature adds/changes any UI surface (web UI, CLI output formatting, error messages shown to users) |
+| ECS / Terraform Deployment Tests | Feature adds or modifies **any** config parameter (env var, setting, Terraform variable, secret) that must flow through the ECS/terraform deployment in `terraform/aws-ecs/` |
+| E2E API Tests | Feature adds a new user-visible workflow that spans multiple endpoints or services |
+
+### Testing Plan Template
+
+Use this template verbatim (fill in the placeholders, remove sections marked "Not Applicable" except to record the justification):
+
+```markdown
+# Testing Plan: {Feature Name}
+
+*Created: {date}*
+*Related LLD: `./lld.md`*
+*Related Issue: `./github-issue.md`*
+
+## Overview
+
+### Scope of Testing
+{1-2 sentences describing what is being tested and why}
+
+### Test Environments
+
+| Environment | Purpose | How to Reach |
+|-------------|---------|--------------|
+| Local (docker-compose) | Primary dev verification | `docker-compose up -d` at repo root |
+| AWS ECS (terraform) | Staging/prod parity | `terraform/aws-ecs/` deployment |
+
+### Prerequisites
+
+- [ ] Registry and Keycloak running (`docker ps | grep -E 'registry\|keycloak'`)
+- [ ] Auth tokens generated: `cd credentials-provider && ./generate_creds.sh`
+- [ ] Token file exists: `ls -la .oauth-tokens/ingress.json`
+- [ ] {Any feature-specific prereqs, e.g. MongoDB seeded with X}
+
+### Shared Variables
+
+```bash
+export REGISTRY_URL="http://localhost"             # or https://registry.<region>.<domain>
+export TOKEN_FILE=".oauth-tokens/ingress.json"
+export ACCESS_TOKEN=$(jq -r '.access_token' "$TOKEN_FILE")
+```
+
+---
+
+## 1. Functional Tests
+
+### 1.1 curl Tests (HTTP API)
+
+For each new or modified endpoint, provide a copy-pasteable curl command, the expected response, and the assertion being verified.
+
+#### Test 1.1.1: {Endpoint description, e.g. "Create resource X"}
+
+**Endpoint:** `POST /api/v1/{path}`
+
+**Command:**
+```bash
+curl -sS -X POST "$REGISTRY_URL/api/v1/{path}" \
+  -H "Authorization: Bearer $ACCESS_TOKEN" \
+  -H "Content-Type: application/json" \
+  -d '{
+        "field1": "value1",
+        "field2": 42
+      }' \
+  | jq
+```
+
+**Expected Status:** `200 OK` (or `201 Created`)
+
+**Expected Response:**
+```json
+{
+  "id": "{id}",
+  "status": "success"
+}
+```
+
+**Assertions:**
+- [ ] Response contains `id` field
+- [ ] `status == "success"`
+- [ ] {Any side effect to verify, e.g. record exists in DB}
+
+**Negative Case:**
+```bash
+# Missing required field should return 400
+curl -sS -X POST "$REGISTRY_URL/api/v1/{path}" \
+  -H "Authorization: Bearer $ACCESS_TOKEN" \
+  -H "Content-Type: application/json" \
+  -d '{}' -w "\n%{http_code}\n"
+```
+Expected: `400` with validation error body.
+
+#### Test 1.1.2: {Next endpoint}
+{Repeat the structure above for each endpoint}
+
+### 1.2 registry_management.py CLI Tests
+
+For each new or modified CLI command exposed via `api/registry_management.py`, provide the exact invocation and expected output.
+
+#### Test 1.2.1: {Command description, e.g. "Register a new feature resource"}
+
+**Command:**
+```bash
+cd api
+uv run python registry_management.py {subcommand} \
+  --token-file "../$TOKEN_FILE" \
+  --registry-url "$REGISTRY_URL" \
+  --{new-param} "{value}"
+```
+
+**Expected Output (key fragments):**
+```
+Successfully created {resource}: <id>
+```
+
+**Assertions:**
+- [ ] Exit code is `0`
+- [ ] Output includes the created resource id
+- [ ] Follow-up `list` command shows the resource
+
+**Follow-up Verification:**
+```bash
+uv run python registry_management.py list \
+  --token-file "../$TOKEN_FILE" \
+  --registry-url "$REGISTRY_URL"
+```
+
+#### Test 1.2.2: {Next command}
+{Repeat the structure above}
+
+---
+
+## 2. Backwards Compatibility Tests
+
+*Include this section if the feature touches any existing endpoint, schema, CLI command, default value, or data model. Otherwise replace with: "**Not Applicable** - feature introduces only net-new surface area: {justification}".*
+
+### 2.1 Existing API Contract
+
+Goal: confirm that existing clients continue to work without code changes.
+
+#### Test 2.1.1: Legacy request shape still accepted
+
+**Command (pre-feature request body):**
+```bash
+curl -sS -X POST "$REGISTRY_URL/api/v1/{existing-endpoint}" \
+  -H "Authorization: Bearer $ACCESS_TOKEN" \
+  -H "Content-Type: application/json" \
+  -d '{
+        "legacy_field": "value"
+      }' | jq
+```
+
+**Assertions:**
+- [ ] Returns `200` (not `400`)
+- [ ] Response contains all previously documented fields
+- [ ] New optional fields either absent or have sensible defaults
+
+### 2.2 Existing CLI Behavior
+
+#### Test 2.2.1: CLI command without new flags behaves as before
+
+```bash
+uv run python registry_management.py {existing-command} \
+  --token-file "../$TOKEN_FILE" \
+  --registry-url "$REGISTRY_URL"
+```
+
+**Assertions:**
+- [ ] Exit code `0`
+- [ ] Output format unchanged (diff against pre-change baseline if available)
+
+### 2.3 Default Behavior When New Config Unset
+
+- [ ] Feature disabled by default (or matches prior behavior) when new env vars are unset
+- [ ] No new required config parameter breaks existing deployments
+
+---
+
+## 3. UX Tests
+
+*Include this section if the feature changes any user-facing surface (web UI, CLI output, error messages). Otherwise replace with: "**Not Applicable** - feature is internal only, with no UX changes."*
+
+### 3.1 Web UI Tests
+
+For each UI change, describe the manual test steps.
+
+#### Test 3.1.1: {UI flow, e.g. "Display new resource in listing"}
+
+**Steps:**
+1. Log in to the registry UI at `$REGISTRY_URL`
+2. Navigate to {page}
+3. Verify {visible element} renders correctly
+4. {Action, e.g. click "Create"}
+5. Verify {expected outcome}
+
+**Assertions:**
+- [ ] Element visible at correct position
+- [ ] No console errors in browser devtools
+- [ ] Responsive behavior at mobile width works
+- [ ] Accessible: keyboard navigation and screen-reader labels present
+
+### 3.2 CLI Output / Error Message Tests
+
+#### Test 3.2.1: Error message is actionable
+
+```bash
+uv run python registry_management.py {command} --invalid-flag bad-value
+```
+
+**Assertions:**
+- [ ] Error clearly states what was invalid
+- [ ] Error suggests the correct usage
+- [ ] No stack trace leaked to user
+
+---
+
+## 4. ECS / Terraform Deployment Tests
+
+*Include this section whenever the feature adds or modifies ANY config parameter (env var, setting, Terraform variable, secret). Otherwise replace with: "**Not Applicable** - feature introduces no new config parameters. Verified by reviewing diff of `registry/core/config.py` and `terraform/aws-ecs/`."*
+
+### 4.1 Terraform Variable Wiring
+
+For each new config parameter, confirm it is plumbed through the ECS deployment.
+
+| Config Parameter | Env Var Name | Added To | Verification Command |
+|------------------|--------------|----------|----------------------|
+| `feature_enabled` | `FEATURE_ENABLED` | `terraform/aws-ecs/ecs.tf` (task definition env block) | `grep FEATURE_ENABLED terraform/aws-ecs/*.tf` |
+| `feature_interval_seconds` | `FEATURE_INTERVAL_SECONDS` | `terraform/aws-ecs/variables.tf` + `ecs.tf` | `grep -n FEATURE_INTERVAL_SECONDS terraform/aws-ecs/` |
+
+### 4.2 Terraform Plan/Apply Verification
+
+```bash
+cd terraform/aws-ecs
+terraform init
+terraform validate
+terraform plan -var 'feature_enabled=true' -var 'feature_interval_seconds=60'
+```
+
+**Assertions:**
+- [ ] `terraform validate` passes
+- [ ] `terraform plan` shows the new variable in the ECS task definition env block
+- [ ] No unintended changes to unrelated resources
+
+### 4.3 Deploy and Verify on ECS
+
+```bash
+cd terraform/aws-ecs
+terraform apply -var 'feature_enabled=true' -var 'feature_interval_seconds=60'
+```
+
+**Post-Deploy Assertions:**
+- [ ] ECS service reaches `RUNNING` state
+- [ ] CloudWatch logs show the feature initialized with the configured values
+- [ ] Health check endpoint returns `200` against the deployed ALB/CloudFront URL
+- [ ] Re-run the Functional Tests from section 1 against the deployed `$REGISTRY_URL`
+
+### 4.4 Rollback Verification
+
+- [ ] `terraform apply` with `feature_enabled=false` disables the feature cleanly
+- [ ] Reverting to the previous task definition restores prior behavior (backwards compat holds in deployed env)
+
+---
+
+## 5. End-to-End API Tests
+
+*Include this section if the feature adds a user-visible workflow that spans multiple endpoints or services. Otherwise replace with: "**Not Applicable** - feature is a single-endpoint change, covered by Functional Tests section 1."*
+
+### 5.1 E2E Scenario: {Scenario Name}
+
+**Goal:** {business outcome being exercised, e.g. "A tenant onboards, registers a server, invokes a tool, and tears down the resources"}
+
+**Setup:**
+```bash
+# Generate token, set env vars (see Shared Variables above)
+export RUN_ID=$(date +%s)
+```
+
+**Steps (each step is executable):**
+
+1. **Create prerequisite resources**
+   ```bash
+   curl -sS -X POST "$REGISTRY_URL/api/v1/{pre-req}" \
+     -H "Authorization: Bearer $ACCESS_TOKEN" \
+     -d '{ "name": "e2e-'$RUN_ID'" }'
+   ```
+
+2. **Exercise the new feature**
+   ```bash
+   curl -sS -X POST "$REGISTRY_URL/api/v1/{new-endpoint}" \
+     -H "Authorization: Bearer $ACCESS_TOKEN" \
+     -d '{ "ref": "e2e-'$RUN_ID'" }'
+   ```
+
+3. **Verify cross-service side effect**
+   ```bash
+   curl -sS "$REGISTRY_URL/api/v1/{downstream-check}/e2e-$RUN_ID" | jq
+   ```
+
+4. **Teardown**
+   ```bash
+   curl -sS -X DELETE "$REGISTRY_URL/api/v1/{pre-req}/e2e-$RUN_ID"
+   ```
+
+**Assertions:**
+- [ ] All steps return expected status codes
+- [ ] Final state matches expected (resource visible in listing, metrics emitted, logs present)
+- [ ] Teardown leaves the system in its original state
+
+### 5.2 Reuse of Existing E2E Harness
+
+If `api/test-management-api-e2e.sh` already exercises adjacent flows, extend it rather than duplicating:
+
+- [ ] Add new test phase to `api/test-management-api-e2e.sh`
+- [ ] Document additions in `api/test-management-api-e2e.md`
+- [ ] Run full harness locally and against the ECS deployment
+
+```bash
+cd api
+./test-management-api-e2e.sh --token-file ../$TOKEN_FILE --registry-url "$REGISTRY_URL"
+```
+
+---
+
+## 6. Test Execution Checklist
+
+Copy this checklist into the PR description when implementing the feature:
+
+- [ ] Section 1 (Functional) - all curl tests pass against local deployment
+- [ ] Section 1 (Functional) - all `registry_management.py` commands succeed
+- [ ] Section 2 (Backwards Compat) - verified or marked Not Applicable with justification
+- [ ] Section 3 (UX) - verified or marked Not Applicable with justification
+- [ ] Section 4 (ECS/Terraform) - verified or marked Not Applicable with justification
+- [ ] Section 5 (E2E) - verified or marked Not Applicable with justification
+- [ ] Unit tests added in `tests/unit/`
+- [ ] Integration tests added in `tests/integration/`
+- [ ] `uv run pytest tests/ -n 8` passes with no regressions
+```
+
+### Guidance for Generating testing.md
+
+1. **Make tests copy-pasteable.** Use the exact env var conventions (`REGISTRY_URL`, `TOKEN_FILE`, `ACCESS_TOKEN`) and match the style of `api/test-management-api-e2e.sh`.
+2. **Cover every new endpoint and every new CLI command.** If the LLD adds three endpoints and two CLI commands, section 1 must have at least five subsections.
+3. **Anchor ECS tests on concrete files.** Reference `terraform/aws-ecs/ecs.tf`, `variables.tf`, and any module under `terraform/aws-ecs/modules/` that the parameter flows through. Do not write generic "deploy and verify" wording - name the files.
+4. **Mark Not Applicable explicitly.** Do not silently omit sections - always include the heading with a short justification, so reviewers see that the category was considered.
+5. **Align with backwards-compat rules.** If the LLD introduces a schema change, the backwards-compat section must test the pre-change request/response shapes.
+6. **Do not invent endpoints or flags.** Every curl URL, every `registry_management.py` flag, and every Terraform variable must exist in the LLD or the current codebase.
+
+
+## Step 9: Present Summary & Seek Guidance
 
 **IMPORTANT:** After completing the design documents and expert review, present a clear summary to the user and ask for guidance on addressing recommendations.
 
@@ -1258,6 +1635,7 @@ Present the following information in a clear, tabular format:
 | GitHub Issue | `.scratchpad/{feature}/github-issue.md` | Issue specification |
 | Low-Level Design | `.scratchpad/{feature}/lld.md` | Technical design |
 | Expert Review | `.scratchpad/{feature}/review.md` | Multi-persona review |
+| Testing Plan | `.scratchpad/{feature}/testing.md` | Functional, backwards-compat, UX, ECS, and E2E tests |
 
 ### Review Verdicts
 
PATCH

echo "Gold patch applied."
