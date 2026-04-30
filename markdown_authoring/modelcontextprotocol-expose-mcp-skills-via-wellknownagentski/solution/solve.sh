#!/usr/bin/env bash
set -euo pipefail

cd /workspace/modelcontextprotocol

# Idempotency guard
if grep -qF "../../../../plugins/mcp-spec/skills/search-mcp-github/SKILL.md" "docs/.mintlify/skills/search-mcp-github/SKILL.md" && grep -qF "license: Apache-2.0" "plugins/mcp-spec/skills/search-mcp-github/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/.mintlify/skills/search-mcp-github/SKILL.md b/docs/.mintlify/skills/search-mcp-github/SKILL.md
@@ -0,0 +1 @@
+../../../../plugins/mcp-spec/skills/search-mcp-github/SKILL.md
\ No newline at end of file
diff --git a/plugins/mcp-spec/skills/search-mcp-github/SKILL.md b/plugins/mcp-spec/skills/search-mcp-github/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: search-mcp-github
 description: Search MCP PRs, issues, and discussions across the modelcontextprotocol GitHub org
+license: Apache-2.0
 user_invocable: true
 arguments:
   - name: topic
PATCH

echo "Gold patch applied."
