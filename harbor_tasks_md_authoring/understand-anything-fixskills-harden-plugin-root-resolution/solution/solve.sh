#!/usr/bin/env bash
set -euo pipefail

cd /workspace/understand-anything

# Idempotency guard
if grep -qF "COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-dashboard 2>/dev/null" "understand-anything-plugin/skills/understand-dashboard/SKILL.md" && grep -qF "**Important:** do **not** assume the plugin root is simply two directories above" "understand-anything-plugin/skills/understand/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/understand-anything-plugin/skills/understand-dashboard/SKILL.md b/understand-anything-plugin/skills/understand-dashboard/SKILL.md
@@ -20,27 +20,50 @@ Start the Understand Anything dashboard to visualize the knowledge graph for the
    ```
 
 3. Find the dashboard code. The dashboard is at `packages/dashboard/` relative to this plugin's root directory. Check these paths in order and use the first that exists:
+   - `${CLAUDE_PLUGIN_ROOT}/packages/dashboard/` (Claude Code runtime root, highest priority)
    - `~/.understand-anything-plugin/packages/dashboard/` (universal symlink, all installs)
-   - `${CLAUDE_PLUGIN_ROOT}/packages/dashboard/` (Claude Code plugin)
-   - Two levels up from this skill file's real path: `../../packages/dashboard/` (self-relative fallback)
+   - Two levels up from `~/.agents/skills/understand-dashboard` real path (self-relative fallback)
+   - Two levels up from `~/.copilot/skills/understand-dashboard` real path (Copilot personal skills fallback)
+   - Common clone-based install roots:
+     - `~/.codex/understand-anything/understand-anything-plugin/packages/dashboard/`
+     - `~/.opencode/understand-anything/understand-anything-plugin/packages/dashboard/`
+     - `~/.pi/understand-anything/understand-anything-plugin/packages/dashboard/`
+     - `~/understand-anything/understand-anything-plugin/packages/dashboard/`
 
    Use the Bash tool to resolve:
    ```bash
    SKILL_REAL=$(realpath ~/.agents/skills/understand-dashboard 2>/dev/null || readlink -f ~/.agents/skills/understand-dashboard 2>/dev/null || echo "")
    SELF_RELATIVE=$([ -n "$SKILL_REAL" ] && cd "$SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
+   COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-dashboard 2>/dev/null || readlink -f ~/.copilot/skills/understand-dashboard 2>/dev/null || echo "")
+   COPILOT_SELF_RELATIVE=$([ -n "$COPILOT_SKILL_REAL" ] && cd "$COPILOT_SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
 
    PLUGIN_ROOT=""
    for candidate in \
-     "$HOME/.understand-anything-plugin" \
      "${CLAUDE_PLUGIN_ROOT}" \
-     "$SELF_RELATIVE"; do
+     "$HOME/.understand-anything-plugin" \
+     "$SELF_RELATIVE" \
+     "$COPILOT_SELF_RELATIVE" \
+     "$HOME/.codex/understand-anything/understand-anything-plugin" \
+     "$HOME/.opencode/understand-anything/understand-anything-plugin" \
+     "$HOME/.pi/understand-anything/understand-anything-plugin" \
+     "$HOME/understand-anything/understand-anything-plugin"; do
      if [ -n "$candidate" ] && [ -d "$candidate/packages/dashboard" ]; then
        PLUGIN_ROOT="$candidate"; break
      fi
    done
 
    if [ -z "$PLUGIN_ROOT" ]; then
-     echo "Error: Cannot find the understand-anything plugin root. Make sure you followed the installation instructions and that ~/.understand-anything-plugin exists."
+     echo "Error: Cannot find the understand-anything plugin root."
+     echo "Checked:"
+     echo "  - ${CLAUDE_PLUGIN_ROOT:-<unset CLAUDE_PLUGIN_ROOT>}"
+     echo "  - $HOME/.understand-anything-plugin"
+     echo "  - ${SELF_RELATIVE:-<unresolved path derived from ~/.agents/skills/understand-dashboard>}"
+     echo "  - ${COPILOT_SELF_RELATIVE:-<unresolved path derived from ~/.copilot/skills/understand-dashboard>}"
+     echo "  - $HOME/.codex/understand-anything/understand-anything-plugin"
+     echo "  - $HOME/.opencode/understand-anything/understand-anything-plugin"
+     echo "  - $HOME/.pi/understand-anything/understand-anything-plugin"
+     echo "  - $HOME/understand-anything/understand-anything-plugin"
+     echo "Make sure you followed the installation instructions for your platform."
      exit 1
    fi
    ```
diff --git a/understand-anything-plugin/skills/understand/SKILL.md b/understand-anything-plugin/skills/understand/SKILL.md
@@ -29,10 +29,49 @@ Determine whether to run a full analysis or incremental update.
      - Verify the resolved path exists and is a directory (run `test -d <path>`). If it does not exist or is not a directory, report an error to the user and **STOP**.
      - Set `PROJECT_ROOT` to the resolved absolute path.
    - If no directory path argument is found, set `PROJECT_ROOT` to the current working directory.
-1.5. **Ensure the plugin is built.** Later phases invoke Node scripts that import `@understand-anything/core`. On a fresh install `packages/core/dist/` does not exist yet — build once. This skill file lives at `<PLUGIN_ROOT>/skills/understand/SKILL.md`, so the plugin root is two directories above it.
+1.5. **Ensure the plugin is built.** Later phases invoke Node scripts that import `@understand-anything/core`. On a fresh install `packages/core/dist/` does not exist yet — build once.
+
+   **Important:** do **not** assume the plugin root is simply two directories above the skill path string. In many installations `~/.agents/skills/understand` is a symlink into the real plugin checkout. Prefer runtime-provided plugin roots first (for Claude), then fall back to universal symlinks, skill symlink resolution, and common clone-based install paths.
+
+   Resolve the plugin root like this:
 
    ```bash
-   PLUGIN_ROOT="<two directories above this SKILL.md>"
+   SKILL_REAL=$(realpath ~/.agents/skills/understand 2>/dev/null || readlink -f ~/.agents/skills/understand 2>/dev/null || echo "")
+   SELF_RELATIVE=$([ -n "$SKILL_REAL" ] && cd "$SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
+   COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand 2>/dev/null || readlink -f ~/.copilot/skills/understand 2>/dev/null || echo "")
+   COPILOT_SELF_RELATIVE=$([ -n "$COPILOT_SKILL_REAL" ] && cd "$COPILOT_SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
+
+   PLUGIN_ROOT=""
+   for candidate in \
+     "${CLAUDE_PLUGIN_ROOT}" \
+     "$HOME/.understand-anything-plugin" \
+     "$SELF_RELATIVE" \
+     "$COPILOT_SELF_RELATIVE" \
+     "$HOME/.codex/understand-anything/understand-anything-plugin" \
+     "$HOME/.opencode/understand-anything/understand-anything-plugin" \
+     "$HOME/.pi/understand-anything/understand-anything-plugin" \
+     "$HOME/understand-anything/understand-anything-plugin"; do
+     if [ -n "$candidate" ] && [ -f "$candidate/package.json" ] && [ -f "$candidate/pnpm-workspace.yaml" ]; then
+       PLUGIN_ROOT="$candidate"
+       break
+     fi
+   done
+
+   if [ -z "$PLUGIN_ROOT" ]; then
+     echo "Error: Cannot find the understand-anything plugin root."
+     echo "Checked:"
+     echo "  - ${CLAUDE_PLUGIN_ROOT:-<unset CLAUDE_PLUGIN_ROOT>}"
+     echo "  - $HOME/.understand-anything-plugin"
+     echo "  - ${SELF_RELATIVE:-<unresolved path derived from ~/.agents/skills/understand>}"
+     echo "  - ${COPILOT_SELF_RELATIVE:-<unresolved path derived from ~/.copilot/skills/understand>}"
+     echo "  - $HOME/.codex/understand-anything/understand-anything-plugin"
+     echo "  - $HOME/.opencode/understand-anything/understand-anything-plugin"
+     echo "  - $HOME/.pi/understand-anything/understand-anything-plugin"
+     echo "  - $HOME/understand-anything/understand-anything-plugin"
+     echo "Make sure the plugin is installed correctly."
+     exit 1
+   fi
+
    if [ ! -f "$PLUGIN_ROOT/packages/core/dist/index.js" ]; then
      cd "$PLUGIN_ROOT" && (pnpm install --frozen-lockfile 2>/dev/null || pnpm install) && pnpm --filter @understand-anything/core build
    fi
PATCH

echo "Gold patch applied."
