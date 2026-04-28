#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sqldef

# Idempotency guard
if grep -qF "* [ ] `make build`  # Ensure all commands are compiled" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -175,6 +175,7 @@ There are markdown files to describe the usage of each command. Keep them up to
 
 Before considering any task complete, run these commands:
 
-* [ ] `make build`      # Ensure it compiles
-* [ ] `make test`       # Run all tests
-* [ ] `gofmt -w .`      # Format the code
+* [ ] `make build`  # Ensure all commands are compiled
+* [ ] `make test`   # Ensure all tests pass
+* [ ] `make lint`   # Ensure the code is linted
+* [ ] `make format` # Ensure the code is formatted
PATCH

echo "Gold patch applied."
