#!/usr/bin/env bash
set -euo pipefail

cd /workspace/llm-agents.nix

# Idempotency guard
if grep -qF "subPackages = [ \".\" ];  # for go find the relevant packages containing the binar" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -45,6 +45,8 @@ buildGoModule rec {
     hash = "sha256-...";  # nix-update updates this
   };
 
+  subPackages = [ "." ];  # for go find the relevant packages containing the binary
+
   vendorHash = "sha256-...";  # nix-update updates this too
 }
 ```
PATCH

echo "Gold patch applied."
