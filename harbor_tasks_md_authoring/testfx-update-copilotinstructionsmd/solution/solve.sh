#!/usr/bin/env bash
set -euo pipefail

cd /workspace/testfx

# Idempotency guard
if grep -qF "- If you are unsure, comment with the temperature and sentiment of the comment, " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -27,7 +27,7 @@ You MUST minimize adding public API surface area but any newly added public API
 Anytime you add a new localization resource, you MUST:
 - Add a corresponding entry in the localization resource file.
 - Add an entry in all `*.xlf` files related to the modified `.resx` file.
-- Do not modify existing entries in '*.xlf' files unless you are also modifying the corresponding `.resx` file.
+- Do not modify existing entries in `*.xlf` files unless you are also modifying the corresponding `.resx` file.
 
 ## Testing Guidelines
 
@@ -39,4 +39,4 @@ Anytime you add a new localization resource, you MUST:
 
 - Let other developers discuss their comments to your PRs, unless something sounds like a direct order to you, don't do changes.
 - Do the changes when you are specifically tagged or mentioned as copilot.
-- If you are unsure comment with the temperature and sentiment of the comment, so we know how to efficiently address you as a member of the team rather than having to tag you.
+- If you are unsure, comment with the temperature and sentiment of the comment, so we know how to efficiently address you as a member of the team rather than having to tag you.
PATCH

echo "Gold patch applied."
