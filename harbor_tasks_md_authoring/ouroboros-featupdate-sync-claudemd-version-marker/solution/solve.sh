#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ouroboros

# Idempotency guard
if grep -qF "sed -i.bak \"s/<!-- ooo:VERSION:.*-->/<!-- ooo:VERSION:$NEW_VERSION -->/\" CLAUDE." "skills/update/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/update/SKILL.md b/skills/update/SKILL.md
@@ -70,18 +70,35 @@ When the user invokes this skill:
    claude plugin update ouroboros@ouroboros
    ```
 
-   c. **Verify**:
+   c. **Verify and update CLAUDE.md version marker**:
    ```bash
-   python3 -c "import ouroboros; print(ouroboros.__version__)"
+   NEW_VERSION=$(python3 -c "import ouroboros; print(ouroboros.__version__)" 2>/dev/null)
+   echo "Installed: v$NEW_VERSION"
+
+   if [ -n "$NEW_VERSION" ] && grep -q "ooo:VERSION" CLAUDE.md 2>/dev/null; then
+     OLD_VERSION=$(grep "ooo:VERSION" CLAUDE.md | sed 's/.*ooo:VERSION:\(.*\) -->/\1/' | tr -d ' ')
+     if [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
+       sed -i.bak "s/<!-- ooo:VERSION:.*-->/<!-- ooo:VERSION:$NEW_VERSION -->/" CLAUDE.md && rm -f CLAUDE.md.bak
+       echo "CLAUDE.md version marker updated: v$OLD_VERSION → v$NEW_VERSION"
+     else
+       echo "CLAUDE.md version marker already up to date (v$NEW_VERSION)"
+     fi
+   fi
    ```
 
+   > **Note**: This only updates the version marker. If the block content itself
+   > changed between versions, the user should run `ooo setup` to regenerate it.
+
 5. **Post-update guidance**:
    ```
    Updated to v0.X.Z
 
    If you have an MCP server running, restart it:
      ouroboros mcp serve --transport stdio
 
+   If CLAUDE.md block content changed, regenerate it:
+     ooo setup
+
    📍 Run `ooo help` to see what's new.
    ```
 
PATCH

echo "Gold patch applied."
