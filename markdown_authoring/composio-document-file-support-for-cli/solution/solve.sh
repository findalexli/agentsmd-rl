#!/usr/bin/env bash
set -euo pipefail

cd /workspace/composio

# Idempotency guard
if grep -qF "`composio run` executes an inline ESM JavaScript/Typescript (bun compatible) sni" "ts/packages/cli/skills/composio-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ts/packages/cli/skills/composio-cli/SKILL.md b/ts/packages/cli/skills/composio-cli/SKILL.md
@@ -38,6 +38,16 @@ composio execute GITHUB_CREATE_AN_ISSUE -d @issue.json
 cat issue.json | composio execute GITHUB_CREATE_AN_ISSUE -d -
 ```
 
+Upload a local file when the tool has a single `file_uploadable` input:
+
+```bash
+composio execute SLACK_UPLOAD_OR_CREATE_A_FILE_IN_SLACK \
+  --file ./image.png \
+  -d '{ channels: "C123" }'
+```
+
+`--file` injects the local path into the tool's single uploadable file field. If a tool has no uploadable file input, or has more than one, use explicit `-d` JSON instead.
+
 Run independent tool calls in parallel:
 
 ```bash
@@ -80,7 +90,7 @@ composio proxy https://api.github.com/user --toolkit github --method GET </dev/n
 
 > **For programmatic calls, LLM workflows, or anything beyond a single tool call — use `composio run`.**
 
-`composio run` executes an inline JavaScript snippet with authenticated `execute()`, `search()`, `proxy()`, and the experimental `experimental_subAgent()` helper pre-injected. No SDK setup required.
+`composio run` executes an inline ESM JavaScript/Typescript (bun compatible) snippet with authenticated `execute()`, `search()`, `proxy()`, and the experimental `experimental_subAgent()` helper pre-injected. No SDK setup required.
 
 Chain multiple tools:
 
PATCH

echo "Gold patch applied."
