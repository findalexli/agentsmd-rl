#!/usr/bin/env bash
set -euo pipefail

cd /workspace/thoth

# Idempotency guard
if grep -qF "8. **GitHub Action supply chain integrity** - pin GitHub Actions in any workflow" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -110,5 +110,6 @@ cd tests && bash run_tests.sh bash
 5. **Follow POSIX syntax** - code must run on all supported shells
 6. **Code style** - for shell code, use lower case with underscore for variable names.
 7. **Code compactness** - no comments in the code, keep the code as minimal and simple as possible - the code should speak for itself
+8. **GitHub Action supply chain integrity** - pin GitHub Actions in any workflow to full-length commit SHAs (not tags); for readability, you may add a comment indicating the corresponding action version next to the SHA
 
 **Trust these instructions**. Only search for information if instructions are incomplete or errors occur not documented here.
PATCH

echo "Gold patch applied."
