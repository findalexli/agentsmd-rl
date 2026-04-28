#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- On init, stored credentials are validated against `/admin/version` with a `Bas" "ui-v2/src/auth/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/src/auth/AGENTS.md b/ui-v2/src/auth/AGENTS.md
@@ -18,8 +18,9 @@ Does NOT implement the login form UI — that lives in `src/routes/`. Does NOT m
 
 - Auth is required when `settings.auth` is any truthy value (not only `"BASIC"`). This means custom auth modes also trigger the auth gate.
 - Credentials are stored as a base64-encoded password in `localStorage` under the key `"prefect-password"`.
-- On init, stored credentials are validated against `/admin/version` with a `Basic` auth header. Invalid credentials are cleared immediately.
-- Session invalidation is event-driven: API middleware dispatches a `"auth:unauthorized"` window event, which `AuthProvider` listens for to reset `isAuthenticated` to `false` without a page reload.
+- On init, stored credentials are validated against `/admin/version` with a `Basic` auth header. Invalid credentials are cleared immediately. A persistent error toast is shown **only on 401** — network errors and other HTTP errors (e.g., 500) do not trigger the toast.
+- Session invalidation is event-driven: API middleware dispatches a `"auth:unauthorized"` window event, which `AuthProvider` listens for to reset `isAuthenticated` to `false` and show a persistent error toast.
+- Auth failure toasts use `id: "auth-failed"` (via `sonner`) for deduplication — multiple rapid auth failures produce only one visible toast.
 
 ## Anti-Patterns
 
PATCH

echo "Gold patch applied."
