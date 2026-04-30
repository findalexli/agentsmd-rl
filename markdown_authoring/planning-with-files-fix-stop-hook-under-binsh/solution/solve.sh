#!/usr/bin/env bash
set -euo pipefail

cd /workspace/planning-with-files

# Idempotency guard
if grep -qF "powershell -ExecutionPolicy Bypass -File \"$SCRIPT_DIR/check-complete.ps1\" 2>/dev" ".codex/skills/planning-with-files/SKILL.md" && grep -qF "powershell -ExecutionPolicy Bypass -File \"$SCRIPT_DIR/check-complete.ps1\" 2>/dev" ".cursor/skills/planning-with-files/SKILL.md" && grep -qF "powershell -ExecutionPolicy Bypass -File \"$SCRIPT_DIR/check-complete.ps1\" 2>/dev" ".kilocode/skills/planning-with-files/SKILL.md" && grep -qF "powershell -ExecutionPolicy Bypass -File \"$SCRIPT_DIR/check-complete.ps1\" 2>/dev" ".opencode/skills/planning-with-files/SKILL.md" && grep -qF "powershell -ExecutionPolicy Bypass -File \"$SCRIPT_DIR/check-complete.ps1\" 2>/dev" "skills/planning-with-files/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.codex/skills/planning-with-files/SKILL.md b/.codex/skills/planning-with-files/SKILL.md
@@ -28,10 +28,28 @@ hooks:
         - type: command
           command: |
             SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
-            if command -v pwsh &> /dev/null && [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
-              pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || bash "$SCRIPT_DIR/check-complete.sh"
+
+            IS_WINDOWS=0
+            if [ "${OS-}" = "Windows_NT" ]; then
+              IS_WINDOWS=1
+            else
+              UNAME_S="$(uname -s 2>/dev/null || echo '')"
+              case "$UNAME_S" in
+                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
+              esac
+            fi
+
+            if [ "$IS_WINDOWS" -eq 1 ]; then
+              if command -v pwsh >/dev/null 2>&1; then
+                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              else
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              fi
             else
-              bash "$SCRIPT_DIR/check-complete.sh"
+              sh "$SCRIPT_DIR/check-complete.sh"
             fi
 ---
 
diff --git a/.cursor/skills/planning-with-files/SKILL.md b/.cursor/skills/planning-with-files/SKILL.md
@@ -28,10 +28,28 @@ hooks:
         - type: command
           command: |
             SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
-            if command -v pwsh &> /dev/null && [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
-              pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || bash "$SCRIPT_DIR/check-complete.sh"
+
+            IS_WINDOWS=0
+            if [ "${OS-}" = "Windows_NT" ]; then
+              IS_WINDOWS=1
+            else
+              UNAME_S="$(uname -s 2>/dev/null || echo '')"
+              case "$UNAME_S" in
+                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
+              esac
+            fi
+
+            if [ "$IS_WINDOWS" -eq 1 ]; then
+              if command -v pwsh >/dev/null 2>&1; then
+                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              else
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              fi
             else
-              bash "$SCRIPT_DIR/check-complete.sh"
+              sh "$SCRIPT_DIR/check-complete.sh"
             fi
 ---
 
diff --git a/.kilocode/skills/planning-with-files/SKILL.md b/.kilocode/skills/planning-with-files/SKILL.md
@@ -28,10 +28,28 @@ hooks:
         - type: command
           command: |
             SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
-            if command -v pwsh &> /dev/null && [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
-              pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || bash "$SCRIPT_DIR/check-complete.sh"
+
+            IS_WINDOWS=0
+            if [ "${OS-}" = "Windows_NT" ]; then
+              IS_WINDOWS=1
+            else
+              UNAME_S="$(uname -s 2>/dev/null || echo '')"
+              case "$UNAME_S" in
+                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
+              esac
+            fi
+
+            if [ "$IS_WINDOWS" -eq 1 ]; then
+              if command -v pwsh >/dev/null 2>&1; then
+                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              else
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              fi
             else
-              bash "$SCRIPT_DIR/check-complete.sh"
+              sh "$SCRIPT_DIR/check-complete.sh"
             fi
 ---
 
diff --git a/.opencode/skills/planning-with-files/SKILL.md b/.opencode/skills/planning-with-files/SKILL.md
@@ -28,10 +28,28 @@ hooks:
         - type: command
           command: |
             SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
-            if command -v pwsh &> /dev/null && [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
-              pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || bash "$SCRIPT_DIR/check-complete.sh"
+
+            IS_WINDOWS=0
+            if [ "${OS-}" = "Windows_NT" ]; then
+              IS_WINDOWS=1
+            else
+              UNAME_S="$(uname -s 2>/dev/null || echo '')"
+              case "$UNAME_S" in
+                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
+              esac
+            fi
+
+            if [ "$IS_WINDOWS" -eq 1 ]; then
+              if command -v pwsh >/dev/null 2>&1; then
+                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              else
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              fi
             else
-              bash "$SCRIPT_DIR/check-complete.sh"
+              sh "$SCRIPT_DIR/check-complete.sh"
             fi
 ---
 
diff --git a/skills/planning-with-files/SKILL.md b/skills/planning-with-files/SKILL.md
@@ -28,10 +28,28 @@ hooks:
         - type: command
           command: |
             SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
-            if command -v pwsh &> /dev/null && [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
-              pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null || bash "$SCRIPT_DIR/check-complete.sh"
+
+            IS_WINDOWS=0
+            if [ "${OS-}" = "Windows_NT" ]; then
+              IS_WINDOWS=1
+            else
+              UNAME_S="$(uname -s 2>/dev/null || echo '')"
+              case "$UNAME_S" in
+                CYGWIN*|MINGW*|MSYS*) IS_WINDOWS=1 ;;
+              esac
+            fi
+
+            if [ "$IS_WINDOWS" -eq 1 ]; then
+              if command -v pwsh >/dev/null 2>&1; then
+                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              else
+                powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||
+                sh "$SCRIPT_DIR/check-complete.sh"
+              fi
             else
-              bash "$SCRIPT_DIR/check-complete.sh"
+              sh "$SCRIPT_DIR/check-complete.sh"
             fi
 ---
 
PATCH

echo "Gold patch applied."
