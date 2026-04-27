#!/usr/bin/env bash
set -euo pipefail

cd /workspace/planning-with-files

# Idempotency guard
if grep -qF "command: \"SD=\\\"${CODEBUDDY_PLUGIN_ROOT:-$HOME/.codebuddy/skills/planning-with-fi" ".codebuddy/skills/planning-with-files/SKILL.md" && grep -qF "command: \"SD=\\\"${CODEX_SKILL_ROOT:-$HOME/.codex/skills/planning-with-files}/scri" ".codex/skills/planning-with-files/SKILL.md" && grep -qF "command: \"SD=\\\"${CURSOR_SKILL_ROOT:-.cursor/skills/planning-with-files}/scripts\\" ".cursor/skills/planning-with-files/SKILL.md" && grep -qF "command: \"SD=\\\"${KILOCODE_SKILL_ROOT:-$HOME/.kilocode/skills/planning-with-files" ".kilocode/skills/planning-with-files/SKILL.md" && grep -qF "command: \"SD=\\\"$HOME/.mastracode/skills/planning-with-files/scripts\\\"; [ -f \\\"$S" ".mastracode/skills/planning-with-files/SKILL.md" && grep -qF "command: \"SD=\\\"${OPENCODE_SKILL_ROOT:-$HOME/.config/opencode/skills/planning-wit" ".opencode/skills/planning-with-files/SKILL.md" && grep -qF "command: \"SD=\\\"${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/" "skills/planning-with-files/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.codebuddy/skills/planning-with-files/SKILL.md b/.codebuddy/skills/planning-with-files/SKILL.md
@@ -17,31 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${CODEBUDDY_PLUGIN_ROOT:-$HOME/.codebuddy/skills/planning-with-files}/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"${CODEBUDDY_PLUGIN_ROOT:-$HOME/.codebuddy/skills/planning-with-files}/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.16.1"
 ---
diff --git a/.codex/skills/planning-with-files/SKILL.md b/.codex/skills/planning-with-files/SKILL.md
@@ -17,31 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${CODEX_SKILL_ROOT:-$HOME/.codex/skills/planning-with-files}/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"${CODEX_SKILL_ROOT:-$HOME/.codex/skills/planning-with-files}/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.16.1"
 ---
diff --git a/.cursor/skills/planning-with-files/SKILL.md b/.cursor/skills/planning-with-files/SKILL.md
@@ -17,31 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${CURSOR_SKILL_ROOT:-.cursor/skills/planning-with-files}/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"${CURSOR_SKILL_ROOT:-.cursor/skills/planning-with-files}/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.16.1"
 ---
diff --git a/.kilocode/skills/planning-with-files/SKILL.md b/.kilocode/skills/planning-with-files/SKILL.md
@@ -17,31 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${KILOCODE_SKILL_ROOT:-$HOME/.kilocode/skills/planning-with-files}/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"${KILOCODE_SKILL_ROOT:-$HOME/.kilocode/skills/planning-with-files}/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.16.1"
 ---
diff --git a/.mastracode/skills/planning-with-files/SKILL.md b/.mastracode/skills/planning-with-files/SKILL.md
@@ -17,32 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${HOME}/.mastracode/skills/planning-with-files/scripts"
-            [ -f "$SCRIPT_DIR/check-complete.sh" ] || SCRIPT_DIR=".mastracode/skills/planning-with-files/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"$HOME/.mastracode/skills/planning-with-files/scripts\"; [ -f \"$SD/check-complete.sh\" ] || SD=\".mastracode/skills/planning-with-files/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.18.1"
 ---
diff --git a/.opencode/skills/planning-with-files/SKILL.md b/.opencode/skills/planning-with-files/SKILL.md
@@ -17,31 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${OPENCODE_SKILL_ROOT:-$HOME/.config/opencode/skills/planning-with-files}/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"${OPENCODE_SKILL_ROOT:-$HOME/.config/opencode/skills/planning-with-files}/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.16.1"
 ---
diff --git a/skills/planning-with-files/SKILL.md b/skills/planning-with-files/SKILL.md
@@ -17,31 +17,7 @@ hooks:
   Stop:
     - hooks:
         - type: command
-          command: |
-            SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
-
-            IS_WINDOWS=0
-            if [ "${OS-}" = "Windows_NT" ]; then
-              IS_WINDOWS=1
-            else
-              UNAME_S="$(uname -s 2>/dev/null || echo '')"
-              case "$UNAME_S" in
-                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
-              esac
-            fi
-
-            if [ "$IS_WINDOWS" -eq 1 ]; then
-              if command -v pwsh >/dev/null 2>&1; then
-                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              else
-                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
-                sh "$SCRIPT_DIR/check-complete.sh"
-              fi
-            else
-              sh "$SCRIPT_DIR/check-complete.sh"
-            fi
+          command: "SD=\"${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$SD/check-complete.ps1\" 2>/dev/null || sh \"$SD/check-complete.sh\""
 metadata:
   version: "2.16.1"
 ---
PATCH

echo "Gold patch applied."
