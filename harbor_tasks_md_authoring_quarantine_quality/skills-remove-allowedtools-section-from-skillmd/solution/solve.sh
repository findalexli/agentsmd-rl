#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "skills/matlab-live-script/SKILL.md" "skills/matlab-live-script/SKILL.md" && grep -qF "skills/matlab-performance-optimizer/SKILL.md" "skills/matlab-performance-optimizer/SKILL.md" && grep -qF "skills/matlab-test-generator/SKILL.md" "skills/matlab-test-generator/SKILL.md" && grep -qF "skills/matlab-uihtml-app-builder/SKILL.md" "skills/matlab-uihtml-app-builder/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/matlab-live-script/SKILL.md b/skills/matlab-live-script/SKILL.md
@@ -2,11 +2,6 @@
 name: matlab-live-script
 description: Create MATLAB plain text Live Scripts (.m files) following specific formatting rules. Use when generating MATLAB scripts, educational MATLAB content, Live Scripts, or when the user requests .m files with rich text formatting.
 license: MathWorks BSD-3-Clause (see LICENSE)
-allowed-tools:
-  - Read
-  - Write
-  - Edit
-  - Bash
 ---
 
 # MATLAB Plain Text Live Script Generator
diff --git a/skills/matlab-performance-optimizer/SKILL.md b/skills/matlab-performance-optimizer/SKILL.md
@@ -2,13 +2,6 @@
 name: matlab-performance-optimizer
 description: Optimize MATLAB code for better performance through vectorization, memory management, and profiling. Use when user requests optimization, mentions slow code, performance issues, speed improvements, or asks to make code faster or more efficient.
 license: MathWorks BSD-3-Clause (see LICENSE)
-allowed-tools:
-  - Read
-  - Write
-  - Edit
-  - Bash
-  - Grep
-  - Glob
 ---
 
 # MATLAB Performance Optimizer
diff --git a/skills/matlab-test-generator/SKILL.md b/skills/matlab-test-generator/SKILL.md
@@ -2,13 +2,6 @@
 name: matlab-test-generator
 description: Create comprehensive MATLAB unit tests using the MATLAB Testing Framework. Use when generating test files, test cases, unit tests, test suites, or when the user requests testing for MATLAB code, functions, or classes.
 license: MathWorks BSD-3-Clause (see LICENSE)
-allowed-tools:
-  - Read
-  - Write
-  - Edit
-  - Bash
-  - Grep
-  - Glob
 ---
 
 # MATLAB Test Generator
diff --git a/skills/matlab-uihtml-app-builder/SKILL.md b/skills/matlab-uihtml-app-builder/SKILL.md
@@ -2,13 +2,6 @@
 name: matlab-uihtml-app-builder
 description: Build interactive web applications using HTML/JavaScript interfaces with MATLAB computational backends via the uihtml component. Use when creating HTML-based MATLAB apps, JavaScript MATLAB interfaces, web UIs with MATLAB, interactive MATLAB GUIs, or when user mentions uihtml, HTML, JavaScript, web apps, or web interfaces.
 license: MathWorks BSD-3-Clause (see LICENSE)
-allowed-tools:
-  - Read
-  - Write
-  - Edit
-  - Bash
-  - Grep
-  - Glob
 ---
 
 # MATLAB uihtml App Builder
PATCH

echo "Gold patch applied."
