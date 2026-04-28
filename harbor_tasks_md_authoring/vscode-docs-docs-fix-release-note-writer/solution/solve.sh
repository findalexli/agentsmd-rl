#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode-docs

# Idempotency guard
if grep -qF "2. **Stable Release Notes**: These notes summarize the key features and improvem" ".github/skills/release-note-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/release-note-writer/SKILL.md b/.github/skills/release-note-writer/SKILL.md
@@ -10,7 +10,7 @@ There are two main types of release notes you can generate using this skill:
 
 1. **Insiders Release Notes**: These notes cover the latest features and updates in the Insiders build of VS Code. They are updated frequently as new features are added. Their format includes sections grouped by the date of the updates. The content is generated based on closed GitHub issues and PRs for a specific milestone.
 
-2. **Stable Release Notes**: These notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature areas. The release is intially created using a template and then updated by the engineering team.
+2. **Stable Release Notes**: These notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature areas. The release is initially created using a template and then updated by the engineering team.
 
 Your task is help generate these release notes based on the provided guidelines, examples, and templates.
 
@@ -71,7 +71,7 @@ The [1.109 release notes](./examples/v1_109.md) are a concrete example of an Ins
 
 ## Stable Release Notes
 
-Stable release notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature areas. The release is intially created using a template and then updated by the engineering team.
+Stable release notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature areas. The release is initially created using a template and then updated by the engineering team.
 
 ### Input parameters
 
PATCH

echo "Gold patch applied."
