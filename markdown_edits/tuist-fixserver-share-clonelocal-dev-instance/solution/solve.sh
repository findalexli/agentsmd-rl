#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tuist

# Idempotent: skip if already applied
if [ -f mise/utilities/dev_instance_env.sh ]; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/workflows/cache.yml b/.github/workflows/cache.yml
index 71c27d476f19..81b239a8c2e1 100644
--- a/.github/workflows/cache.yml
+++ b/.github/workflows/cache.yml
@@ -30,6 +30,7 @@ defaults:
 env:
   GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   MISE_GITHUB_ATTESTATIONS: 0
+  MISE_CEILING_PATHS: ${{ github.workspace }}

 jobs:
   format:
diff --git a/.github/workflows/gradle-cache-acceptance.yml b/.github/workflows/gradle-cache-acceptance.yml
index 4b5d0fa4c9c0..0c5c637de18c 100644
--- a/.github/workflows/gradle-cache-acceptance.yml
+++ b/.github/workflows/gradle-cache-acceptance.yml
@@ -121,8 +121,9 @@ jobs:
         working-directory: server
         run: |
           MIX_ENV=dev mix phx.server &
+          server_url="${TUIST_SERVER_URL:-http://localhost:8080}"
           for i in {1..30}; do
-            if curl -sf http://localhost:8080 >/dev/null 2>&1; then
+            if curl -sf "$server_url" >/dev/null 2>&1; then
               echo "Main server is ready"
               break
             fi
@@ -133,8 +134,9 @@ jobs:
         working-directory: cache
         run: |
           MIX_ENV=dev mix phx.server &
+          cache_port="${TUIST_CACHE_PORT:-8087}"
           for i in {1..30}; do
-            if nc -z localhost 8087 2>/dev/null; then
+            if nc -z localhost "$cache_port" 2>/dev/null; then
               echo "Cache server is ready"
               break
             fi
@@ -143,5 +145,5 @@ jobs:
           done
       - name: Run Gradle cache acceptance test
         env:
-          SERVER_URL: http://localhost:8080
+          SERVER_URL: ${{ env.TUIST_SERVER_URL }}
         run: mise run --no-prepare e2e gradle_cache
diff --git a/.gitignore b/.gitignore
index f29816287365..7b65149863d5 100644
--- a/.gitignore
+++ b/.gitignore
@@ -103,6 +103,7 @@ generated_fixtures
 Tuist.xcworkspace
 node_modules
 Fixture
+/.tuist-dev-instance

 Tuist/Dependencies/SwiftPackageManager
 Tuist/Dependencies/graph.json
diff --git a/cache/README.md b/cache/README.md
index bc52837878d6..2100807b7d71 100644
--- a/cache/README.md
+++ b/cache/README.md
@@ -58,7 +58,7 @@ mix test

 ## Development

-The service runs on port 4000 by default in development mode.
+The service uses a clone-local suffix from `.tuist-dev-instance` in development mode through mise shell env. That suffix scopes the cache port and the main server URL it talks to, so one repo clone can run its own paired `server/` and `cache/` instances without colliding with other clones.

 ## Architecture

diff --git a/cache/config/runtime.exs b/cache/config/runtime.exs
index 03c2b103a6d2..96337b05b7d1 100644
--- a/cache/config/runtime.exs
+++ b/cache/config/runtime.exs
@@ -1,5 +1,16 @@
 import Config

+if config_env() == :dev do
+  cache_port = String.to_integer(System.get_env("TUIST_CACHE_PORT") || "8087")
+  server_url = System.get_env("TUIST_CACHE_SERVER_URL") || "http://localhost:8080"
+
+  config :cache, CacheWeb.Endpoint,
+    url: [host: "localhost", port: cache_port, scheme: "http"],
+    http: [ip: {0, 0, 0, 0}, port: cache_port]
+
+  config :cache, server_url: server_url
+end
+
 if config_env() == :prod do
   secret_key_base =
     System.get_env("SECRET_KEY_BASE") ||
diff --git a/cache/config/test.exs b/cache/config/test.exs
index 67a6a3215bd4..504b62d4afc8 100644
--- a/cache/config/test.exs
+++ b/cache/config/test.exs
@@ -2,6 +2,9 @@ import Config

 alias Ecto.Adapters.SQL.Sandbox

+test_port = String.to_integer(System.get_env("TUIST_CACHE_TEST_PORT") || "4002")
+test_storage_dir = System.get_env("TUIST_CACHE_TEST_STORAGE_DIR") || "/tmp/test_cas"
+
 config :cache, Cache.Guardian,
   issuer: "tuist",
   secret_key: "test_guardian_secret_key_at_least_64_characters_long_for_test_purposes"
@@ -29,7 +32,7 @@ config :cache, Cache.Repo,
 config :cache, Cache.SQLiteBuffer, shutdown_ms: 0, flush_interval_ms: to_timeout(hour: 1), flush_timeout_ms: 50_000

 config :cache, CacheWeb.Endpoint,
-  http: [ip: {127, 0, 0, 1}, port: 4002],
+  http: [ip: {127, 0, 0, 1}, port: test_port],
   secret_key_base: "test_secret_key_base_at_least_64_characters_long_for_security_purposes",
   server: false

@@ -47,7 +50,7 @@ config :cache, :s3,

 config :cache,
   server_url: "http://localhost:8080",
-  storage_dir: "/tmp/test_cas",
+  storage_dir: test_storage_dir,
   api_key: "test-secret-key"

 config :logger, level: :warning
diff --git a/cache/mise.toml b/cache/mise.toml
index 92407c40ddbc..1c4584e5eee0 100644
--- a/cache/mise.toml
+++ b/cache/mise.toml
@@ -1,4 +1,5 @@
 [env]
+_.source = "{{config_root}}/../mise/utilities/dev_instance_env.sh"
 SECRET_KEY_BASE = "3QgyMMP1pcg9+d5Gn3n1/TMciiogjysBmPg1Dm+pT+Hfag38TUm0Q7pHfC7NpZpL"

 [tools]
diff --git a/mise.toml b/mise.toml
index 4f8725486492..cc62aa169c0f 100644
--- a/mise.toml
+++ b/mise.toml
@@ -17,6 +17,7 @@
     postinstall = "{{config_root}}/mise/tasks/install.sh"

 [env]
+    _.source = "{{config_root}}/mise/utilities/dev_instance_env.sh"
     TUIST_CACHE_CONCURRENCY_LIMIT="none"
     # Elixir recommends half of the number of cores: https://elixir-lang.org/blog/2025/10/16/elixir-v1-19-0-released/
     MIX_OS_DEPS_COMPILE_PARTITION_COUNT=4
diff --git a/mise/utilities/dev_instance_env.sh b/mise/utilities/dev_instance_env.sh
new file mode 100644
index 000000000000..fbef613ead46
--- /dev/null
+++ b/mise/utilities/dev_instance_env.sh
@@ -0,0 +1,57 @@
+if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
+  SCRIPT_PATH="${BASH_SOURCE[0]}"
+elif [[ -n "${ZSH_VERSION:-}" ]]; then
+  SCRIPT_PATH="${(%):-%x}"
+else
+  SCRIPT_PATH="${0}"
+fi
+
+SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"
+PROJECT_ROOT="${MISE_PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
+INSTANCE_FILE="${PROJECT_ROOT}/.tuist-dev-instance"
+
+validate_suffix() {
+  local suffix="$1"
+
+  [[ "$suffix" =~ ^[0-9]+$ ]] || return 1
+  (( suffix >= 1 && suffix <= 999 ))
+}
+
+ensure_suffix() {
+  local suffix=""
+
+  if [[ -n "${TUIST_DEV_INSTANCE:-}" ]]; then
+    suffix="${TUIST_DEV_INSTANCE}"
+  elif [[ -s "${INSTANCE_FILE}" ]]; then
+    suffix="$(tr -d '[:space:]' < "${INSTANCE_FILE}")"
+  else
+    suffix="$(awk 'BEGIN { srand(); print int(100 + rand() * 900) }')"
+  fi
+
+  validate_suffix "${suffix}" || {
+    echo "Invalid dev instance suffix '${suffix}'. Expected an integer between 1 and 999." >&2
+    return 1
+  }
+
+  printf '%s' "${suffix}" > "${INSTANCE_FILE}"
+  printf '%s' "${suffix}"
+}
+
+suffix="$(ensure_suffix)"
+test_partition="${MIX_TEST_PARTITION:-}"
+
+export TUIST_DEV_INSTANCE="${suffix}"
+export TUIST_SERVER_PORT="$((8080 + suffix))"
+export TUIST_SERVER_URL="http://localhost:${TUIST_SERVER_PORT}"
+export TUIST_SERVER_POSTGRES_DB="tuist_development_${suffix}"
+export TUIST_SERVER_CLICKHOUSE_DB="tuist_development_${suffix}"
+export TUIST_CACHE_PORT="$((8087 + suffix))"
+export TUIST_CACHE_SERVER_URL="${TUIST_SERVER_URL}"
+export TUIST_MINIO_API_PORT="$((9095 + suffix))"
+export TUIST_MINIO_CONSOLE_PORT="$((9098 + suffix))"
+export TUIST_SERVER_TEST_PORT="$((4002 + suffix))"
+export TUIST_SERVER_TEST_POSTGRES_DB="tuist_test${test_partition}_${suffix}"
+export TUIST_SERVER_TEST_CLICKHOUSE_DB="tuist_test${test_partition}_${suffix}"
+export TUIST_CACHE_TEST_PORT="$((4003 + suffix))"
+export TUIST_CACHE_TEST_POSTGRES_DB="cache_test_${suffix}"
+export TUIST_CACHE_TEST_STORAGE_DIR="/tmp/test_cas_${suffix}"
diff --git a/server/README.md b/server/README.md
index b6d6da2c4c38..4ffdfd29d09a 100644
--- a/server/README.md
+++ b/server/README.md
@@ -23,7 +23,7 @@ Contributions to the Tuist Server require signing a Contributor License Agreemen
 1. Install dependencies: `mise run install`
 1. Create and set up the database: `mise run db:setup`
 1. Run the server: `mise run dev`
-1. Open `http://localhost:8080` in your browser and log in with the pre-made test user account:
+1. Open the clone-specific local URL in your browser and log in with the pre-made test user account. With `mise activate` enabled, each repo clone persists its own numeric suffix in `.tuist-dev-instance`, which scopes the local service ports, MinIO ports, and server databases. For example, a suffix of `443` yields `http://localhost:8523`:

 ```
 Email: tuistrocks@tuist.dev
@@ -36,8 +36,6 @@ Pass: tuistrocks
 #### To run additional features
 1. Clone the repository: `https://github.com/tuist/tuist.git`.
 1. Go to `tuist/examples/xcode/generated_ios_app_with_frameworks`.
-1. Change the url in `Tuist/Config.swift` to `http://localhost:8080`.
+1. Change the url in `Tuist/Config.swift` to the clone-specific local URL, for example `http://localhost:8523`.
 1. Run `tuist auth` to authenticate.
 1. You are now connected to the local Tuist Server!  You can try running `tuist cache` and see the binaries being uploaded.
-
-
diff --git a/server/config/runtime.exs b/server/config/runtime.exs
index 772c79521e54..02e8bff9b6c0 100644
--- a/server/config/runtime.exs
+++ b/server/config/runtime.exs
@@ -169,16 +169,28 @@ if env == :dev do
     for {env_var, key} <- [
           {"DATABASE_USERNAME", :username},
           {"DATABASE_PASSWORD", :password},
-          {"DATABASE_HOST", :hostname}
+          {"DATABASE_HOST", :hostname},
+          {"TUIST_SERVER_POSTGRES_DB", :database}
         ],
         value = System.get_env(env_var),
         do: {key, value}

   config :tuist, Tuist.Repo, dev_db_config
+
+  if clickhouse_database = System.get_env("TUIST_SERVER_CLICKHOUSE_DB") do
+    config :tuist, Tuist.ClickHouseRepo, database: clickhouse_database
+    config :tuist, Tuist.IngestRepo, database: clickhouse_database
+  end
 end

 if Enum.member?([:prod, :stag, :can, :dev], env) do
-  port = "8080"
+  port =
+    if env == :dev do
+      String.to_integer(System.get_env("TUIST_SERVER_PORT") || "8080")
+    else
+      8080
+    end
+
   app_url = Tuist.Environment.app_url([route_type: :app], secrets)
   %{host: app_url_host, port: app_url_port, scheme: app_url_scheme} = URI.parse(app_url)

diff --git a/server/config/test.exs b/server/config/test.exs
index ce116b364bb8..ce9012295013 100644
--- a/server/config/test.exs
+++ b/server/config/test.exs
@@ -1,5 +1,12 @@
 import Config

+test_postgres_db = System.get_env("TUIST_SERVER_TEST_POSTGRES_DB") || "tuist_test#{System.get_env("MIX_TEST_PARTITION")}"
+
+test_clickhouse_db =
+  System.get_env("TUIST_SERVER_TEST_CLICKHOUSE_DB") || "tuist_test#{System.get_env("MIX_TEST_PARTITION")}"
+
+test_port = String.to_integer(System.get_env("TUIST_SERVER_TEST_PORT") || "4002")
+
 # Only in tests, remove the complexity from the password hashing algorithm
 config :bcrypt_elixir, :log_rounds, 1

@@ -24,7 +31,7 @@ config :tuist, Oban, testing: :manual
 config :tuist, Tuist.ClickHouseRepo,
   hostname: "localhost",
   port: 8123,
-  database: "tuist_test#{System.get_env("MIX_TEST_PARTITION")}",
+  database: test_clickhouse_db,
   # Workaround for ClickHouse lazy materialization bug with projections
   # https://github.com/ClickHouse/ClickHouse/issues/80201
   settings: [readonly: 1, query_plan_optimize_lazy_materialization: 0]
@@ -32,7 +39,7 @@ config :tuist, Tuist.ClickHouseRepo,
 config :tuist, Tuist.IngestRepo,
   hostname: "localhost",
   port: 8123,
-  database: "tuist_test#{System.get_env("MIX_TEST_PARTITION")}",
+  database: test_clickhouse_db,
   flush_interval_ms: 5000,
   max_buffer_size: 100_000,
   pool_size: 5,
@@ -53,7 +60,7 @@ config :tuist, Tuist.Repo,
   username: "postgres",
   password: "postgres",
   hostname: "localhost",
-  database: "tuist_test#{System.get_env("MIX_TEST_PARTITION")}",
+  database: test_postgres_db,
   pool: Ecto.Adapters.SQL.Sandbox,
   pool_size: System.schedulers_online() * 2,
   queue_target: 5000,
@@ -62,7 +69,7 @@ config :tuist, Tuist.Repo,
 # We don't run a server during test. If one is required,
 # you can enable the server option below.
 config :tuist, TuistWeb.Endpoint,
-  http: [ip: {127, 0, 0, 1}, port: 4002],
+  http: [ip: {127, 0, 0, 1}, port: test_port],
   secret_key_base: "pbaHQK0N946e06chs5G1/RUJnkI//2QshGgUvJQkADTV3AiQHV/dXlLdjnaQxtxx",
   server: false

diff --git a/server/lib/tuist/environment.ex b/server/lib/tuist/environment.ex
index fcd2eb58f0be..2286080df60a 100644
--- a/server/lib/tuist/environment.ex
+++ b/server/lib/tuist/environment.ex
@@ -282,7 +282,11 @@ defmodule Tuist.Environment do
     if dev_use_remote_storage?() do
       get([:s3, :endpoint], secrets)
     else
-      get([:local_s3_endpoint], secrets) || "http://localhost:9095"
+      System.get_env("TUIST_LOCAL_S3_ENDPOINT") ||
+        case System.get_env("TUIST_MINIO_API_PORT") do
+          port when is_binary(port) -> "http://localhost:#{port}"
+          _ -> get([:local_s3_endpoint], secrets) || "http://localhost:9095"
+        end
     end
   end

@@ -356,7 +360,10 @@ defmodule Tuist.Environment do
   end

   def minio_console_port(secrets \\ secrets()) do
-    get([:minio, :console_port], secrets, default_value: 9098)
+    case System.get_env("TUIST_MINIO_CONSOLE_PORT") do
+      port when is_binary(port) -> String.to_integer(port)
+      _ -> get([:minio, :console_port], secrets, default_value: 9098)
+    end
   end

   def mautic_username(secrets \\ secrets()) do
@@ -664,11 +671,18 @@ defmodule Tuist.Environment do
       # on-premis instance, it should point to the production routes.
       URI.to_string(%{URI.parse(get_url(:production)) | path: path})
     else
-      url = get([:app, :url], secrets) || "http://localhost:8080"
-      URI.to_string(%{URI.parse(url) | path: path})
+      URI.to_string(%{URI.parse(app_base_url(secrets)) | path: path})
     end
   end

+  defp app_base_url(secrets) do
+    get([:app, :url], secrets) || default_app_url()
+  end
+
+  defp default_app_url do
+    if dev?(), do: System.get_env("TUIST_SERVER_URL") || "http://localhost:8080", else: "http://localhost:8080"
+  end
+
   defp get_route_info(path) do
     case Phoenix.Router.route_info(TuistWeb.Router, "GET", path, "") do
       :error -> nil
diff --git a/server/mise.toml b/server/mise.toml
index 35486d51ed6d..b4c51230ddde 100644
--- a/server/mise.toml
+++ b/server/mise.toml
@@ -1,6 +1,10 @@
 [env]
+_.source = "{{config_root}}/../mise/utilities/dev_instance_env.sh"
 TUIST_SECRET_KEY_BASE = "rpux4+W/oBey0drSFOctyIbppOG2A9VUUuTMC1WaM8xZgYxA6gg4yryG/LkOoqkj"

+[hooks]
+  postinstall = "{{config_root}}/mise/tasks/install.sh"
+
 [tools]
   pnpm = "10.17.1"
   node = "24.11.0"
diff --git a/server/mise/tasks/db/migrate.sh b/server/mise/tasks/db/migrate.sh
index 56e629f6c0af..0c532b0ebf54 100755
--- a/server/mise/tasks/db/migrate.sh
+++ b/server/mise/tasks/db/migrate.sh
@@ -3,4 +3,4 @@

 set -euo pipefail

- mix ecto.migrate
+mix ecto.migrate

PATCH

echo "Patch applied successfully."
