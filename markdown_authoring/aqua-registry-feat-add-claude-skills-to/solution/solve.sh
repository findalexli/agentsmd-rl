#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aqua-registry

# Idempotency guard
if grep -qF "description: Fetch the document of aqua from the other repository aquaproj/aqua." ".agents/skills/fetch-doc/SKILL.md" && grep -qF "description: Review changes. Use this skill when adding or changing pkgs/**/*.ya" ".agents/skills/review-change/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/fetch-doc/SKILL.md b/.agents/skills/fetch-doc/SKILL.md
@@ -0,0 +1,19 @@
+---
+name: Fetch aqua Document
+description: Fetch the document of aqua from the other repository aquaproj/aqua. This skill is useful when you want to know the specification of aqua.
+---
+
+The document of aqua is hosted at https://github.com/aquaproj/aqua.
+So please checkout the repository and refer the document.
+
+```sh
+mkdir -p .ai
+if [ ! -d .ai/aqua ]; Then
+  git clone https://github.com/aquaproj/aqua .ai/aqua
+fi
+cd .ai/aqua
+git pull origin main
+```
+
+Then please see .ai/aqua/website/docs.
+Especially, about the registry settings, please see .ai/aqua/website/docs/reference/registry-config/\*.md.
diff --git a/.agents/skills/review-change/SKILL.md b/.agents/skills/review-change/SKILL.md
@@ -0,0 +1,6 @@
+---
+name: review-change
+description: Review changes. Use this skill when adding or changing pkgs/**/*.yaml
+---
+
+Please review pkgs/\*_/_.yaml according to AGENTS.md
PATCH

echo "Gold patch applied."
