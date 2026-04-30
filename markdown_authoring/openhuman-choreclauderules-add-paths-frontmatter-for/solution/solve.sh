#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openhuman

# Idempotency guard
if grep -qF "- \"app/src-tauri/**\"" ".claude/rules/03-platform-setup-windows.md" && grep -qF "- \"app/src-tauri/**\"" ".claude/rules/04-platform-setup-macos.md" && grep -qF "- \"app/src-tauri/gen/android/**\"" ".claude/rules/05-platform-setup-android.md" && grep -qF "- \"app/src-tauri/gen/apple/**\"" ".claude/rules/06-platform-setup-ios.md" && grep -qF "- \"app/src-tauri/**\"" ".claude/rules/07-rust-backend-guide.md" && grep -qF "- \"app/vite.config.*\"" ".claude/rules/08-frontend-guide.md" && grep -qF "- \"**/capabilities/**\"" ".claude/rules/09-permissions-capabilities.md" && grep -qF "- \"**/tailwind.config.*\"" ".claude/rules/12-design-system.md" && grep -qF "- \"app/src-tauri/src/lib.rs\"" ".claude/rules/13-backend-auth-implementation.md" && grep -qF "- \"**/tauri.conf.json\"" ".claude/rules/14-deep-link-platform-guide.md" && grep -qF "- \"app/src/components/settings/**\"" ".claude/rules/15-settings-modal-system.md" && grep -qF "- \"app/src-tauri/src/lib.rs\"" ".claude/rules/16-macos-background-execution.md" && grep -qF "- \"app/src/providers/SkillProvider.tsx\"" ".claude/rules/17-skills-memory-inference-flow.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/03-platform-setup-windows.md b/.claude/rules/03-platform-setup-windows.md
@@ -1,3 +1,9 @@
+---
+paths:
+  - "app/src-tauri/**"
+  - "src-tauri/**"
+---
+
 # Windows Platform Setup
 
 ## Prerequisites
diff --git a/.claude/rules/04-platform-setup-macos.md b/.claude/rules/04-platform-setup-macos.md
@@ -1,3 +1,9 @@
+---
+paths:
+  - "app/src-tauri/**"
+  - "src-tauri/**"
+---
+
 # macOS Platform Setup
 
 ## Prerequisites
diff --git a/.claude/rules/05-platform-setup-android.md b/.claude/rules/05-platform-setup-android.md
@@ -1,3 +1,9 @@
+---
+paths:
+  - "src-tauri/gen/android/**"
+  - "app/src-tauri/gen/android/**"
+---
+
 # Android Platform Setup
 
 ## Prerequisites
diff --git a/.claude/rules/06-platform-setup-ios.md b/.claude/rules/06-platform-setup-ios.md
@@ -1,3 +1,9 @@
+---
+paths:
+  - "src-tauri/gen/apple/**"
+  - "app/src-tauri/gen/apple/**"
+---
+
 # iOS Platform Setup
 
 ## Prerequisites
diff --git a/.claude/rules/07-rust-backend-guide.md b/.claude/rules/07-rust-backend-guide.md
@@ -1,3 +1,11 @@
+---
+paths:
+  - "app/src-tauri/**"
+  - "src-tauri/**"
+  - "src/**/*.rs"
+  - "**/Cargo.toml"
+---
+
 # Rust Backend Guide
 
 ## Structure
diff --git a/.claude/rules/08-frontend-guide.md b/.claude/rules/08-frontend-guide.md
@@ -1,3 +1,11 @@
+---
+paths:
+  - "app/src/**"
+  - "app/*.ts"
+  - "app/*.tsx"
+  - "app/vite.config.*"
+---
+
 # Frontend Development Guide - Crypto Community Platform
 
 ## Overview
diff --git a/.claude/rules/09-permissions-capabilities.md b/.claude/rules/09-permissions-capabilities.md
@@ -1,3 +1,9 @@
+---
+paths:
+  - "**/capabilities/**"
+  - "**/tauri.conf.json"
+---
+
 # Permissions and Capabilities
 
 ## Overview
diff --git a/.claude/rules/12-design-system.md b/.claude/rules/12-design-system.md
@@ -1,3 +1,10 @@
+---
+paths:
+  - "app/src/**/*.tsx"
+  - "app/src/**/*.css"
+  - "**/tailwind.config.*"
+---
+
 # Design System - Crypto Community Platform
 
 ## Design Philosophy
diff --git a/.claude/rules/13-backend-auth-implementation.md b/.claude/rules/13-backend-auth-implementation.md
@@ -1,3 +1,12 @@
+---
+paths:
+  - "**/auth/**"
+  - "**/*auth*.ts"
+  - "**/*auth*.tsx"
+  - "**/*auth*.rs"
+  - "app/src-tauri/src/lib.rs"
+---
+
 # Backend Authentication Implementation Guide
 
 ## Overview
diff --git a/.claude/rules/14-deep-link-platform-guide.md b/.claude/rules/14-deep-link-platform-guide.md
@@ -1,3 +1,10 @@
+---
+paths:
+  - "**/*deep*link*"
+  - "**/tauri.conf.json"
+  - "app/src-tauri/**"
+---
+
 # Deep Link Platform Guide
 
 ## Overview
diff --git a/.claude/rules/15-settings-modal-system.md b/.claude/rules/15-settings-modal-system.md
@@ -1,3 +1,8 @@
+---
+paths:
+  - "app/src/components/settings/**"
+---
+
 # Settings Modal System - URL-Based Modal Architecture
 
 ## Overview
diff --git a/.claude/rules/16-macos-background-execution.md b/.claude/rules/16-macos-background-execution.md
@@ -1,3 +1,10 @@
+---
+paths:
+  - "app/src-tauri/src/lib.rs"
+  - "**/Info.plist"
+  - "**/tauri.conf.json"
+---
+
 # macOS Background Execution - Menu Bar & Autostart
 
 ## Overview
diff --git a/.claude/rules/17-skills-memory-inference-flow.md b/.claude/rules/17-skills-memory-inference-flow.md
@@ -1,3 +1,12 @@
+---
+paths:
+  - "**/skills/**"
+  - "**/memory/**"
+  - "src/openhuman/**"
+  - "app/src/providers/SkillProvider.tsx"
+  - "app/src/lib/ai/**"
+---
+
 # Skills → Memory Layer → Agent Inference: Full Flow
 
 ## Overview
PATCH

echo "Gold patch applied."
