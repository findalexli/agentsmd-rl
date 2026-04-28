#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gram

# Idempotency guard
if grep -qF "| `gram-management-api`         | Designing or modifying management API endpoint" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -107,6 +107,9 @@ Activate a skill when your task falls within its scope.
 | `frontend`                    | Working on the React frontends in `client/` or `elements/`                 |
 | `vercel-react-best-practices` | Optimizing React performance, reviewing components for best practices      |
 | `gram-functions`              | Understanding or modifying the Gram Functions serverless execution feature |
+| `gram-management-api`         | Designing or modifying management API endpoints (Goa design, impl)         |
+| `gram-audit-logging`          | Recording or exposing audit events via the auditlogs management API        |
+| `gram-rbac`                   | Adding or enforcing authorization scopes, grants, or roles                 |
 | `mise-tasks`                  | Creating or editing mise task scripts in `.mise-tasks/`                    |
 | `datadog`                     | Investigating errors, performance, incidents, or telemetry via Datadog     |
 | `datadog-insights`            | Running the full Gram production health digest and posting it to Slack     |
PATCH

echo "Gold patch applied."
