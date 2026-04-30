#!/usr/bin/env bash
set -euo pipefail

cd /workspace/observal

# Idempotency guard
if grep -qF "**Future resource-based access control** will follow PostHog's annotation patter" "ee/AGENTS.md" && grep -qF "There is NO `web/ee/` directory. Enterprise frontend code lives here in `web/src" "web/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ee/AGENTS.md b/ee/AGENTS.md
@@ -62,6 +62,23 @@ Each event → row in ClickHouse `audit_log` table with actor info, resource det
 
 `ee/plugins/__init__.py` — future home for Grafana, Prometheus, Datadog, and SIEM integrations.
 
+## Frontend architecture
+
+There is NO separate `web/ee/` directory. Enterprise frontend code lives in `web/src/` alongside core code, gated by `useDeploymentConfig()`.
+
+This follows the industry-standard pattern (Langfuse, PostHog, Infisical, Lago all do this). The `ee/` boundary is for backend licensing — the frontend is AGPL and gates features server-side, not by directory.
+
+**How enterprise features are gated in the frontend:**
+- `useDeploymentConfig()` hook returns `{ deploymentMode, ssoEnabled, samlEnabled }`
+- Pages check `deploymentMode === "enterprise"` and show upgrade prompts if not
+- SSO button in login page: conditional on `ssoEnabled`
+- Enterprise settings section: conditional on `deploymentMode`
+- API filters results server-side — frontend reads what it's given
+
+**Enterprise-only admin pages** (audit log viewer, diagnostics, SCIM config) should be regular pages in `web/src/app/(admin)/` that check deployment mode and show an upgrade prompt when not enterprise. Do NOT create a `web/ee/` directory.
+
+**Future resource-based access control** will follow PostHog's annotation pattern: include `user_access_level` on every API response object. The API filters results by team membership; the frontend reads the annotation. No CASL or client-side policy engine needed initially.
+
 ## Directory layout
 
 ```
diff --git a/web/AGENTS.md b/web/AGENTS.md
@@ -79,6 +79,19 @@ pnpm lint         # ESLint
 pnpm test:e2e     # Playwright e2e tests (requires running API + Docker stack)
 ```
 
+## Enterprise feature gating
+
+There is NO `web/ee/` directory. Enterprise frontend code lives here in `web/src/`, gated server-side via `useDeploymentConfig()`. This follows the Langfuse/PostHog/Infisical pattern — the `ee/` boundary is backend-only.
+
+**Current enterprise conditionals:**
+- `src/app/(auth)/login/page.tsx` — SSO button shown when `ssoEnabled`
+- `src/app/(admin)/settings/page.tsx` — enterprise settings section shown when `deploymentMode === "enterprise"`
+- `src/hooks/use-deployment-config.ts` — fetches `{ deploymentMode, ssoEnabled, samlEnabled }` from `/api/v1/config/public`
+
+**Pattern for new enterprise pages:** Add regular pages in `src/app/(admin)/` that check deployment mode and show an upgrade prompt when not enterprise. Don't duplicate pages or create separate directories.
+
+**Future resource-based access control:** API will include `user_access_level` on response objects (PostHog annotation pattern). Frontend reads the annotation — no client-side policy engine needed.
+
 ## Conventions
 
 - No Tailwind config file — Tailwind CSS 4 uses `globals.css` for all design tokens
PATCH

echo "Gold patch applied."
