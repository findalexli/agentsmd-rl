#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bencher

# Idempotency guard
if grep -qF "The only acceptable use of a shell script is as an ultra-lightweight wrapper aro" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -122,6 +122,7 @@ cargo build --no-default-features
 ## API Documentation
 
 The API uses Dropshot and generates an OpenAPI spec at `services/api/openapi.json`.
+Whenever changes are made to the API, `cargo gen-types` should be run to update the spec.
 
 ## Database
 
@@ -147,6 +148,16 @@ ARCH=arm64 docker compose --file docker/docker-compose.yml up --build
 - `bencher_boundary` - Statistical analysis for threshold detection
 - `bencher_valid` - Input validation types
 
+## Scripts and Tasks
+
+Shell scripts are to be used very sparingly.
+Instead of using shell scripts, tasks are created in the `tasks/` directory.
+These tasks are invoked using a Cargo `alias` in `.cargo/config.toml`.
+
+Administrative specific tasks that are only run locally and not in CI/CD are located in the catch all `xtask` crate.
+
+The only acceptable use of a shell script is as an ultra-lightweight wrapper around a shell command, like `git` or `docker`.
+
 ## Bencher Documentation
 
 Documentation about how to use Bencher is available locally at `services/console/src/content/`
PATCH

echo "Gold patch applied."
