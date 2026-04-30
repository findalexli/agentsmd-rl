#!/usr/bin/env bash
set -euo pipefail

cd /workspace/activepieces

# Idempotency guard
if grep -qF "- **All customer-facing UI must be white-labeled.** Sign-in/signup pages, email " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -62,6 +62,18 @@
 
 - Always run `npm run lint-dev` as part of any verification step before considering a task complete.
 
+## White-Labeling & Edition Paths
+
+- **All customer-facing UI must be white-labeled.** Sign-in/signup pages, email templates, logos, and any user-visible branding must use the platform's configured appearance (name, colors, logos) — never hardcode "Activepieces" in user-facing surfaces.
+- **Test across all edition paths.** Every customer-facing feature must be verified on:
+  - **Community Edition** (self-hosted, `AP_EDITION=ce`) — no custom branding, open-source plan
+  - **Enterprise Edition** (self-hosted, `AP_EDITION=ee`) — custom branding behind `customAppearanceEnabled` flag
+  - **Cloud Freemium** (`AP_EDITION=cloud`, standard plan) — always applies platform branding
+  - **Cloud Self-Serve Paid** (`AP_EDITION=cloud`, upgraded plan) — same as freemium with higher limits
+  - **Cloud Enterprise** (`AP_EDITION=cloud`, enterprise plan) — full feature set
+- **Appearance is edition-gated.** Community always uses the default theme. Cloud always applies custom branding. Enterprise requires `platform.plan.customAppearanceEnabled`. See `packages/server/api/src/app/ee/helper/appearance-helper.ts`.
+- **Feature gating pattern:** Backend uses `platformMustHaveFeatureEnabled()` middleware (returns 402). Frontend uses `LockedFeatureGuard` component and `enabled: platform.plan.<flag>` on queries.
+
 ## Useful Links
 
 - [Database Migrations Playbook](https://www.activepieces.com/docs/handbook/engineering/playbooks/database-migration)
PATCH

echo "Gold patch applied."
