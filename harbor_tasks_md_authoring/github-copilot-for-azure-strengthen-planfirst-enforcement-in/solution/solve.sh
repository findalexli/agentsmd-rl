#!/usr/bin/env bash
set -euo pipefail

cd /workspace/github-copilot-for-azure

# Idempotency guard
if grep -qF "1. **Plan first \u2014 MANDATORY** \u2014 You MUST physically write an initial `.azure/dep" "plugin/skills/azure-prepare/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugin/skills/azure-prepare/SKILL.md b/plugin/skills/azure-prepare/SKILL.md
@@ -4,7 +4,7 @@ description: "Prepare Azure apps for deployment (infra Bicep/Terraform, azure.ya
 license: MIT
 metadata:
   author: Microsoft
-  version: "1.1.9"
+  version: "1.1.11"
 ---
 
 # Azure Prepare
@@ -28,7 +28,7 @@ Activate this skill when user wants to:
 
 ## Rules
 
-1. **Plan first** — Create `.azure/deployment-plan.md` **in the workspace root directory** (not the session-state folder) before any code generation
+1. **Plan first — MANDATORY** — You MUST physically write an initial `.azure/deployment-plan.md` **skeleton in the workspace root directory** (not the session-state folder) **as your very first action** — before any code generation or execution begins. Write the skeleton immediately, then populate it progressively as Phase 1 analysis and research unfold; finalize it with all decisions at Phase 1 Step 6. This file must exist on disk throughout. azure-validate and azure-deploy depend on it and will fail without it. Do not skip or defer this step.
 2. **Get approval** — Present plan to user before execution
 3. **Research before generating** — Load references and invoke related skills
 4. **Update plan progressively** — Mark steps complete as you go
@@ -45,13 +45,15 @@ Activate this skill when user wants to:
 > **YOU MUST CREATE A PLAN BEFORE DOING ANY WORK**
 >
 > 1. **STOP** — Do not generate any code, infrastructure, or configuration yet
-> 2. **PLAN** — Follow the Planning Phase below to create `.azure/deployment-plan.md`
-> 3. **CONFIRM** — Present the plan to the user and get approval
+> 2. **CREATE SKELETON** - Write an initial `.azure/deployment-plan.md` skeleton to disk **immediately** (before any code generation or execution begins), then populate it progressively as Phase 1 steps 1-5 reveal details; finalize it at Step 6
+> 3. **CONFIRM** — Present the completed plan to the user and get approval
 > 4. **EXECUTE** — Only after approval, execute the plan step by step
 >
 > The `.azure/deployment-plan.md` file is the **source of truth** for this workflow and for azure-validate and azure-deploy skills. Without it, those skills will fail.
 >
-> ⚠️ **CRITICAL: `.azure/deployment-plan.md` must be created inside the workspace root** (e.g., `/tmp/my-project/.azure/deployment-plan.md`), not in the session-state folder. This is the deployment plan artifact read by azure-validate and azure-deploy. **You must create this.**
+> ⚠️ **CRITICAL: `.azure/deployment-plan.md` must be WRITTEN TO DISK inside the workspace root** (e.g., `/tmp/my-project/.azure/deployment-plan.md`), not in the session-state folder. Use a file-write tool to create this file. This is the deployment plan artifact read by azure-validate and azure-deploy. **You MUST create this file — do not proceed without it.**
+>
+> ⛔ **Critical:** Skipping the plan file creation will cause azure-validate and azure-deploy to fail. This requirement has no exceptions.
 
 ---
 
@@ -97,7 +99,7 @@ Create `.azure/deployment-plan.md` by completing these steps. Do NOT generate an
 | 3 | **Scan Codebase** — Identify components, technologies, dependencies | [scan.md](references/scan.md) |
 | 4 | **Select Recipe** — Choose AZD (default), AZCLI, Bicep, or Terraform | [recipe-selection.md](references/recipe-selection.md) |
 | 5 | **Plan Architecture** — Select stack + map components to Azure services | [architecture.md](references/architecture.md) |
-| 6 | **Write Plan** — Generate `.azure/deployment-plan.md` with all decisions | [plan-template.md](references/plan-template.md) |
+| 6 | **Finalize Plan (MANDATORY)** - Use a file-write tool to finalize `.azure/deployment-plan.md` with all decisions from steps 1-5. Update the skeleton written at the start of Phase 1 with the complete content. The file must be fully populated before you present the plan to the user. | [plan-template.md](references/plan-template.md) |
 | 7 | **Present Plan** — Show plan to user and ask for approval | `.azure/deployment-plan.md` |
 | 8 | **Destructive actions require `ask_user`** | [Global Rules](references/global-rules.md) |
 
PATCH

echo "Gold patch applied."
