#!/usr/bin/env bash
set -euo pipefail

cd /workspace/realm

# Idempotency guard
if grep -qF "The majority of our rust codebase is in the `implants/` directory & workspaces. " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -8,6 +8,10 @@ Welcome to our repository! Most commands need to be run from the root of the pro
   * Our user interface is located in `tavern/internal/www` and we managed dependencies within that directory using `npm`
 * `implants/` contains Rust code that is deployed to target machines, such as our agent located in `implants/imix`.
 
+## Rust
+
+The majority of our rust codebase is in the `implants/` directory & workspaces. When adding dependencies to crates within this workspace, please add them to the workspace root and have the crate use the workspace dependency, in order to centralize version management. ALWAYS RUN `cargo fmt` WHEN MAKING RUST CHANGES, OR CI WILL FAIL.
+
 ## Golang Tests
 
 To run all Golang tests in our repository, please run `go test ./...` from the project root.
PATCH

echo "Gold patch applied."
