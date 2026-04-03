#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tuist

# Idempotent: skip if already applied
if grep -q 'assign(:dev?, Environment.dev?())' server/lib/tuist_web/live/user_login_live.ex 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docs/docs/en/contributors/code/server.md b/docs/docs/en/contributors/code/server.md
index 8838b6ffb335..009e7b01db08 100644
--- a/docs/docs/en/contributors/code/server.md
+++ b/docs/docs/en/contributors/code/server.md
@@ -27,9 +27,6 @@ mise install
 brew services start postgresql@16
 mise run clickhouse:start

-# Minimal secrets
-export TUIST_SECRET_KEY_BASE="$(mix phx.gen.secret)"
-
 # Install dependencies + set up the database
 mise run install

@@ -37,8 +34,10 @@ mise run install
 mise run dev
 ```

+Open `http://localhost:8080` in your browser. In development, the login page includes a **Log in as test user** button that signs you in with the pre-made account (`tuistrocks@tuist.dev` / `tuistrocks`).
+
 > [!NOTE]
-> First-party developers load encrypted secrets from `priv/secrets/dev.key`. External contributors won't have that key, and that's fine. The server still runs locally with `TUIST_SECRET_KEY_BASE`, but OAuth, Stripe, and other integrations remain disabled.
+> First-party developers can load encrypted secrets from `priv/secrets/dev.key`. External contributors don't need this key — the server runs locally without it. OAuth, Stripe, and other third-party integrations will be disabled, but core functionality works.

 ### Tests and formatting {#tests-and-formatting}

diff --git a/server/README.md b/server/README.md
index 35854bca4cbc..b6d6da2c4c38 100644
--- a/server/README.md
+++ b/server/README.md
@@ -15,24 +15,24 @@ Contributions to the Tuist Server require signing a Contributor License Agreemen

 ### Set up

-1. Clone the repository: `git clone https://github.com/tuist/server.git`.
+1. Clone the repository: `git clone https://github.com/tuist/tuist.git`.
 1. Open the folder: `cd server`.
-1. Get the private key from 1Password.
-1. Create a `priv/secrets/dev.key` file and add the key to decrypt the secrets needed for development.
-1. Install additional system dependencies with: `mise install`.
+1. Install system dependencies with: `mise install`.
 1. Start Postgres with: `brew services start postgresql@16`.
 1. Start ClickHouse with: `mise run clickhouse:start`
-1. Create a new database with: `mise run db:create`.
-1. Load the data into database with: `mise run db:load`.
-1. Seed your database with data: `mise run db:seed`.
+1. Install dependencies: `mise run install`
+1. Create and set up the database: `mise run db:setup`
 1. Run the server: `mise run dev`
-1. We already have a pre-made user account that you can use to test the server:
+1. Open `http://localhost:8080` in your browser and log in with the pre-made test user account:

 ```
 Email: tuistrocks@tuist.dev
 Pass: tuistrocks
 ```

+> [!NOTE]
+> First-party developers can load encrypted secrets from `priv/secrets/dev.key`. External contributors don't need this key — the server runs locally without it. OAuth, Stripe, and other third-party integrations will be disabled, but core functionality works.
+
 #### To run additional features
 1. Clone the repository: `https://github.com/tuist/tuist.git`.
 1. Go to `tuist/examples/xcode/generated_ios_app_with_frameworks`.
diff --git a/server/lib/tuist_web/live/user_login_live.ex b/server/lib/tuist_web/live/user_login_live.ex
index 41ccf58ca97b..be166206623f 100644
--- a/server/lib/tuist_web/live/user_login_live.ex
+++ b/server/lib/tuist_web/live/user_login_live.ex
@@ -21,6 +21,7 @@ defmodule TuistWeb.UserLoginLive do
       |> assign(:okta_configured?, Environment.okta_oauth_configured?())
       |> assign(:apple_configured?, Environment.apple_oauth_configured?())
       |> assign(:tuist_hosted?, Environment.tuist_hosted?())
+      |> assign(:dev?, Environment.dev?())

     {
       :ok,
@@ -175,6 +176,25 @@ defmodule TuistWeb.UserLoginLive do
               tabindex={4}
             />
           </.form>
+          <form
+            :if={@dev?}
+            action={~p"/users/log_in"}
+            method="post"
+            style="display: contents;"
+          >
+            <input type="hidden" name="_csrf_token" value={Phoenix.Controller.get_csrf_token()} />
+            <input type="hidden" name="user[email]" value="tuistrocks@tuist.dev" />
+            <input type="hidden" name="user[password]" value="tuistrocks" />
+            <button
+              type="submit"
+              class="noora-button"
+              data-variant="secondary"
+              data-size="large"
+              style="width: 100%;"
+            >
+              <span>{dgettext("dashboard_auth", "Log in as test user")}</span>
+            </button>
+          </form>
         </div>
         <div data-part="bottom-link">
           <span>{dgettext("dashboard_auth", "Don't have an account?")}</span>
diff --git a/server/priv/gettext/dashboard_auth.pot b/server/priv/gettext/dashboard_auth.pot
index 7d3438e97603..9bb0b0410fb4 100644
--- a/server/priv/gettext/dashboard_auth.pot
+++ b/server/priv/gettext/dashboard_auth.pot
@@ -127,14 +127,14 @@ msgstr ""
 msgid "Discover how selective testing is reducing your test time."
 msgstr ""

-#: lib/tuist_web/live/user_login_live.ex:180
+#: lib/tuist_web/live/user_login_live.ex:190
 #, elixir-autogen, elixir-format
 msgid "Don't have an account?"
 msgstr ""

 #: lib/tuist_web/live/sso_login_live.ex:71
 #: lib/tuist_web/live/user_forgot_password_live.ex:54
-#: lib/tuist_web/live/user_login_live.ex:137
+#: lib/tuist_web/live/user_login_live.ex:138
 #: lib/tuist_web/live/user_okta_login_live.ex:74
 #: lib/tuist_web/live/user_registration_live.ex:148
 #, elixir-autogen, elixir-format
@@ -156,7 +156,7 @@ msgstr ""
 msgid "Explore how binary caching is enhancing your build times."
 msgstr ""

-#: lib/tuist_web/live/user_login_live.ex:168
+#: lib/tuist_web/live/user_login_live.ex:169
 #, elixir-autogen, elixir-format
 msgid "Forgot password?"
 msgstr ""
@@ -187,14 +187,14 @@ msgstr ""
 msgid "Interested in SSO?"
 msgstr ""

-#: lib/tuist_web/live/user_login_live.ex:161
+#: lib/tuist_web/live/user_login_live.ex:162
 #, elixir-autogen, elixir-format
 msgid "Keep me logged in"
 msgstr ""

 #: lib/tuist_web/live/sso_login_live.ex:79
 #: lib/tuist_web/live/user_login_live.ex:17
-#: lib/tuist_web/live/user_login_live.ex:174
+#: lib/tuist_web/live/user_login_live.ex:175
 #: lib/tuist_web/live/user_okta_login_live.ex:82
 #: lib/tuist_web/live/user_registration_live.ex:192
 #, elixir-autogen, elixir-format
@@ -202,7 +202,7 @@ msgid "Log in"
 msgstr ""

 #: lib/tuist_web/live/sso_login_live.ex:54
-#: lib/tuist_web/live/user_login_live.ex:47
+#: lib/tuist_web/live/user_login_live.ex:48
 #: lib/tuist_web/live/user_okta_login_live.ex:57
 #, elixir-autogen, elixir-format
 msgid "Log in to Tuist"
@@ -244,7 +244,7 @@ msgstr ""
 msgid "Okta log in"
 msgstr ""

-#: lib/tuist_web/live/user_login_live.ex:148
+#: lib/tuist_web/live/user_login_live.ex:149
 #: lib/tuist_web/live/user_registration_live.ex:158
 #, elixir-autogen, elixir-format
 msgid "Password"
@@ -286,7 +286,7 @@ msgstr ""
 msgid "Selective testing"
 msgstr ""

-#: lib/tuist_web/live/user_login_live.ex:185
+#: lib/tuist_web/live/user_login_live.ex:195
 #: lib/tuist_web/live/user_registration_live.ex:181
 #: lib/tuist_web/live/user_registration_live.ex:264
 #, elixir-autogen, elixir-format
@@ -313,7 +313,7 @@ msgstr ""
 #: lib/tuist_web/live/sso_login_live.ex:46
 #: lib/tuist_web/live/user_confirmation_live.ex:18
 #: lib/tuist_web/live/user_forgot_password_live.ex:23
-#: lib/tuist_web/live/user_login_live.ex:39
+#: lib/tuist_web/live/user_login_live.ex:40
 #: lib/tuist_web/live/user_okta_login_live.ex:49
 #: lib/tuist_web/live/user_registration_live.ex:67
 #: lib/tuist_web/live/user_registration_live.ex:210
@@ -369,7 +369,7 @@ msgstr ""
 msgid "We'll send a password reset link to your inbox"
 msgstr ""

-#: lib/tuist_web/live/user_login_live.ex:49
+#: lib/tuist_web/live/user_login_live.ex:50
 #, elixir-autogen, elixir-format
 msgid "Welcome back! Please log in to continue"
 msgstr ""
@@ -450,3 +450,8 @@ msgstr ""
 #, elixir-autogen, elixir-format
 msgid "and"
 msgstr ""
+
+#: lib/tuist_web/live/user_login_live.ex:185
+#, elixir-autogen, elixir-format
+msgid "Log in as test user"
+msgstr ""

PATCH

echo "Patch applied successfully."
