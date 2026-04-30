#!/usr/bin/env bash
set -euo pipefail

cd /workspace/officecli

# Idempotency guard
if grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "SKILL.md" && grep -qF "Follow the install section in `reference/officecli-pptx-min.md` section 0." "skills/morph-ppt/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/morph-ppt/reference/officecli-pptx-min.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-academic-paper/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-data-dashboard/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-docx/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-financial-model/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-pitch-deck/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-pptx/SKILL.md" && grep -qF "If `officecli` is still not found after first install, open a new terminal and r" "skills/officecli-xlsx/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -7,25 +7,29 @@ description: Create, analyze, proofread, and modify Office documents (.docx, .xl
 
 AI-friendly CLI for .docx, .xlsx, .pptx. Single binary, no dependencies, no Office installation needed.
 
-## Install & Update
+## Install
 
-Same command for both install and upgrade:
+If `officecli` is not installed:
 
-```bash
-# macOS / Linux
-curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
+`macOS / Linux`
 
-# Windows (PowerShell)
-irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+```bash
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
+fi
 ```
 
-After installation, run `source ~/.zshrc` (macOS) or `source ~/.bashrc` (Linux) to make the `officecli` command available.
+`Windows (PowerShell)`
 
-Running bare `officecli` (no arguments) also triggers auto-install.
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
 
 Verify: `officecli --version`
 
-officecli auto-updates daily in the background.
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
 
 ---
 
diff --git a/skills/morph-ppt/SKILL.md b/skills/morph-ppt/SKILL.md
@@ -105,9 +105,9 @@ For every morph transition, plan the slide pair BEFORE writing any code. Use a t
 - Do **not** click "Open with system app" during generation, to avoid file lock / write conflicts.
 - Use clear, direct language and make this a concrete warning, not an optional suggestion.
 
-**FIRST: Ensure latest officecli version**
+**FIRST: Install `officecli` if needed**
 
-Follow the installation check in `reference/officecli-pptx-min.md` section 0 (checks version and upgrades only if needed).
+Follow the install section in `reference/officecli-pptx-min.md` section 0.
 
 **IMPORTANT: Use morph-helpers for reliable workflow**
 
diff --git a/skills/morph-ppt/reference/officecli-pptx-min.md b/skills/morph-ppt/reference/officecli-pptx-min.md
@@ -3,37 +3,31 @@ name: officecli-commands
 description: OfficeCli Command Reference — PPT generation and validation commands
 ---
 
-# OfficeCli PPT Command Reference
+# OfficeCLI PPT Command Reference
 
 ## 0) BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-# Check if installed
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    # macOS/Linux
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    # Check if update needed
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT → $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
+```
 
-# Verify version
-officecli --version
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
 ```
 
-**Why:** This ensures you have the latest features and bug fixes before starting work.
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
 
 ---
 
@@ -77,7 +71,7 @@ officecli set demo.pptx '/slide[1]/shape[1]' --prop gradient="linear:90:FF0000,0
 officecli validate demo.pptx
 ```
 
-**For comprehensive reference:** https://github.com/iOfficeAI/OfficeCli/wiki/agent-guide
+**For comprehensive reference:** https://github.com/iOfficeAI/OfficeCLI/wiki/agent-guide
 
 ---
 
diff --git a/skills/officecli-academic-paper/SKILL.md b/skills/officecli-academic-paper/SKILL.md
@@ -12,26 +12,28 @@ Create formally structured Word documents with Table of Contents, equations (LaT
 
 ## BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT -> $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 
 ## Use When
diff --git a/skills/officecli-data-dashboard/SKILL.md b/skills/officecli-data-dashboard/SKILL.md
@@ -12,26 +12,28 @@ Create professional, formula-driven Excel dashboards from CSV or tabular data. T
 
 ## BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT -> $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 
 ## Use When
diff --git a/skills/officecli-docx/SKILL.md b/skills/officecli-docx/SKILL.md
@@ -9,26 +9,28 @@ description: "Use this skill any time a .docx file is involved -- as input, outp
 
 ## BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT → $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 # officecli: v1.0.23
 
diff --git a/skills/officecli-financial-model/SKILL.md b/skills/officecli-financial-model/SKILL.md
@@ -20,26 +20,28 @@ Build formula-driven, multi-sheet financial models from scratch in Excel. Every
 
 ## BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT -> $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 
 ## Use When
diff --git a/skills/officecli-pitch-deck/SKILL.md b/skills/officecli-pitch-deck/SKILL.md
@@ -12,26 +12,28 @@ Create professional pitch presentations from scratch -- investor decks, product
 
 ## BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT -> $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 
 ## Use When
diff --git a/skills/officecli-pptx/SKILL.md b/skills/officecli-pptx/SKILL.md
@@ -19,26 +19,28 @@ description: "Use this skill any time a .pptx file is involved -- as input, outp
 > ```
 > 如果看到 `no matches found`，说明引号缺失。
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT → $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 
 ## Quick Reference
diff --git a/skills/officecli-xlsx/SKILL.md b/skills/officecli-xlsx/SKILL.md
@@ -8,26 +8,28 @@ description: "Use this skill any time a .xlsx file is involved -- as input, outp
 
 ## BEFORE YOU START (CRITICAL)
 
-**Every time before using officecli, run this check:**
+**If `officecli` is not installed:**
+
+`macOS / Linux`
 
 ```bash
-if ! command -v officecli &> /dev/null; then
-    echo "Installing officecli..."
-    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    # Windows: irm https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.ps1 | iex
-else
-    CURRENT=$(officecli --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
-    LATEST=$(curl -fsSL https://api.github.com/repos/iOfficeAI/OfficeCLI/releases/latest | grep '"tag_name"' | sed -E 's/.*"v?([0-9.]+)".*/\1/')
-    if [ "$CURRENT" != "$LATEST" ]; then
-        echo "Upgrading officecli $CURRENT → $LATEST..."
-        curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCli/main/install.sh | bash
-    else
-        echo "officecli $CURRENT is up to date"
-    fi
+if ! command -v officecli >/dev/null 2>&1; then
+    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
 fi
-officecli --version
 ```
 
+`Windows (PowerShell)`
+
+```powershell
+if (-not (Get-Command officecli -ErrorAction SilentlyContinue)) {
+    irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
+}
+```
+
+Verify: `officecli --version`
+
+If `officecli` is still not found after first install, open a new terminal and run the verify command again.
+
 ---
 
 ## Quick Reference
PATCH

echo "Gold patch applied."
