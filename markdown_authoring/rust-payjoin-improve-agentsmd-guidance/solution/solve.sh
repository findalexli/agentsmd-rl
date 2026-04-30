#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rust-payjoin

# Idempotency guard
if grep -qF "Tools are provided by nix via direnv. Do not install tools globally." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -5,6 +5,12 @@ For the full human guide see [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md
 Nightly Rust toolchain (`rust-toolchain.toml`) — required for `cargo fmt`
 unstable options.
 
+## Tooling
+
+Tools are provided by nix via direnv. Do not install tools globally.
+If you need a new tool, add it to the devshell in `flake.nix` so
+others can reproduce.
+
 ## Commit Rules
 
 Every commit must pass CI independently.
@@ -53,4 +59,6 @@ bash contrib/update-lock-files.sh
 
 ## AI Disclosure
 
-Required in PR body. Do **not** add `Co-Authored-By` in commits.
+Add to PR body: `Disclosure: co-authored by <agent-name>`
+
+Do **not** add `Co-Authored-By` in commits.
PATCH

echo "Gold patch applied."
