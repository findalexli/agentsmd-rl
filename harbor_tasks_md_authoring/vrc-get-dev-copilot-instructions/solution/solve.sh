#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vrc-get

# Idempotency guard
if grep -qF "- After completing code and commit, please add changelog entry. please note that" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,4 @@
+If you're writing code:
+- Please don't make localization for locales other than en / ja. I cannot review those locales.
+- Run cargo clippy for lints and cargo fmt for format before commit.
+- After completing code and commit, please add changelog entry. please note that the numbers in the changelog file is pull request number, not a issue number.
PATCH

echo "Gold patch applied."
