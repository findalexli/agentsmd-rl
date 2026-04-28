#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xurl

# Idempotency guard
if grep -qF "Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated " "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -11,40 +11,42 @@ description: A curl-like CLI tool for making authenticated requests to the X (Tw
 
 ## Prerequisites
 
+This skill requires the `xurl` CLI utility: <https://github.com/xdevplatform/xurl>.
+
 Before using any command you must be authenticated. Run `xurl auth status` to check.
 
+### Secret Safety (Mandatory)
+
+- Never read, print, parse, summarize, upload, or send `~/.xurl` (or copies of it) to the LLM context.
+- Never ask the user to paste credentials/tokens into chat.
+- The user must fill `~/.xurl` with required secrets manually on their own machine.
+- Do not recommend or execute auth commands with inline secrets in agent/LLM sessions.
+- Warn that using CLI secret options in agent sessions can leak credentials (prompt/context, logs, shell history).
+- Never use `--verbose` / `-v` in agent/LLM sessions; it can expose sensitive headers/tokens in output.
+- Sensitive flags that must never be used in agent commands: `--bearer-token`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--client-id`, `--client-secret`.
+- To verify whether at least one app with credentials is already registered, run: `xurl auth status`.
+
 ### Register an app (recommended)
 
-```bash
-# Register your X API app credentials (stored in ~/.xurl)
-xurl auth apps add my-app --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
+App credential registration must be done manually by the user outside the agent/LLM session.
+After credentials are registered, authenticate with:
 
-# Then authenticate
+```bash
 xurl auth oauth2
 ```
 
-You can register multiple apps and switch between them:
+For multiple pre-configured apps, switch between them:
 ```bash
-xurl auth apps add prod-app --client-id PROD_ID --client-secret PROD_SECRET
-xurl auth apps add dev-app  --client-id DEV_ID  --client-secret DEV_SECRET
 xurl auth default prod-app          # set default app
 xurl auth default prod-app alice    # set default app + user
 xurl --app dev-app /2/users/me      # one-off override
 ```
 
 ### Other auth methods
 
-```bash
-# OAuth 1.0a
-xurl auth oauth1 \
-  --consumer-key KEY --consumer-secret SECRET \
-  --access-token TOKEN --token-secret SECRET
-
-# App‑only bearer token
-xurl auth app --bearer-token TOKEN
-```
+Examples with inline secret flags are intentionally omitted. If OAuth1 or app-only auth is needed, the user must run those commands manually outside agent/LLM context.
 
-Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated tokens. Once authenticated, every command below will auto‑attach the right `Authorization` header.
+Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated tokens. Do not read this file through the agent/LLM. Once authenticated, every command below will auto‑attach the right `Authorization` header.
 
 ---
 
@@ -83,9 +85,9 @@ Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated
 | Upload media | `xurl media upload path/to/file.mp4` |
 | Media status | `xurl media status MEDIA_ID` |
 | **App Management** | |
-| Register app | `xurl auth apps add NAME --client-id ID --client-secret SEC` |
+| Register app | Manual, outside agent (do not pass secrets via agent) |
 | List apps | `xurl auth apps list` |
-| Update app creds | `xurl auth apps update NAME --client-id ID` |
+| Update app creds | Manual, outside agent (do not pass secrets via agent) |
 | Remove app | `xurl auth apps remove NAME` |
 | Set default (interactive) | `xurl auth default` |
 | Set default (command) | `xurl auth default APP_NAME [USERNAME]` |
@@ -248,7 +250,7 @@ These flags work on every command:
 | `--app` | | Use a specific registered app for this request (overrides default) |
 | `--auth` | | Force auth type: `oauth1`, `oauth2`, or `app` |
 | `--username` | `-u` | Which OAuth2 account to use (if you have multiple) |
-| `--verbose` | `-v` | Print full request/response headers |
+| `--verbose` | `-v` | Forbidden in agent/LLM sessions (can leak auth headers/tokens) |
 | `--trace` | `-t` | Add `X-B3-Flags: 1` trace header |
 
 ---
@@ -360,11 +362,8 @@ xurl timeline -n 20
 
 ### Set up multiple apps
 ```bash
-# Register two apps
-xurl auth apps add prod --client-id PROD_ID --client-secret PROD_SECRET
-xurl auth apps add staging --client-id STG_ID --client-secret STG_SECRET
-
-# Authenticate users on each
+# App credentials must already be configured manually outside agent/LLM context.
+# Authenticate users on each pre-configured app
 xurl auth default prod
 xurl auth oauth2                       # authenticates on prod app
 
@@ -392,7 +391,7 @@ xurl --app staging /2/users/me         # one-off request against staging
 - **Rate limits:** The X API enforces rate limits per endpoint. If you get a 429 error, wait and retry. Write endpoints (post, reply, like, repost) have stricter limits than read endpoints.
 - **Scopes:** OAuth 2.0 tokens are requested with broad scopes. If you get a 403 on a specific action, your token may lack the required scope — re‑run `xurl auth oauth2` to get a fresh token.
 - **Token refresh:** OAuth 2.0 tokens auto‑refresh when expired. No manual intervention needed.
-- **Multiple apps:** Register multiple apps with `xurl auth apps add`. Each app has its own isolated credentials and tokens. Switch with `xurl auth default` or `--app`.
+- **Multiple apps:** Each app has its own isolated credentials and tokens. Configure credentials manually outside agent/LLM context, then switch with `xurl auth default` or `--app`.
 - **Multiple accounts:** You can authenticate multiple OAuth 2.0 accounts per app and switch between them with `--username` / `-u` or set a default with `xurl auth default APP USER`.
 - **Default user:** When no `-u` flag is given, xurl uses the default user for the active app (set via `xurl auth default`). If no default user is set, it uses the first available token.
-- **Token storage:** `~/.xurl` is YAML. Each app stores its own credentials and tokens.
+- **Token storage:** `~/.xurl` is YAML. Each app stores its own credentials and tokens. Never read or send this file to LLM context.
PATCH

echo "Gold patch applied."
