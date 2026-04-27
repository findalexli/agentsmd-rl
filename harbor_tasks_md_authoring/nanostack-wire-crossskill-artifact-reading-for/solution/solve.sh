#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "- `scope_mode` \u2192 if /think said \"reduce,\" plan the smallest version. If \"expand," "plan/SKILL.md" && grep -qF "If the plan specifies product standards (shadcn/ui, Tailwind, dark mode, specifi" "qa/SKILL.md" && grep -qF "- **`risks[]`** \u2192 create a risk checklist. For each risk, actively probe the cod" "review/SKILL.md" && grep -qF "Then read project config: `bin/init-config.sh`. Use `detected` to scope which ch" "security/SKILL.md" && grep -qF "If a review artifact exists, check that all **blocking** findings have been addr" "ship/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -11,6 +11,17 @@ You turn validated ideas into executable steps. Every file gets named. Every ste
 
 ### 1. Understand the Request
 
+- **Read the /think artifact** if one exists for this project:
+  ```bash
+  bin/find-artifact.sh think 2
+  ```
+  If found, extract and use:
+  - `key_risk` → add to your Risks section. This was already validated by /think.
+  - `narrowest_wedge` → this is the scope constraint. Don't plan beyond it.
+  - `out_of_scope` items from /think → pre-populate your Out of Scope section.
+  - `scope_mode` → if /think said "reduce," plan the smallest version. If "expand," plan bigger.
+  - `premise_validated` → if false, flag it. Don't plan for an unvalidated premise.
+
 - Check git history for recent changes in the affected area — someone may have already started this work or made decisions you need to respect.
 - If the request is ambiguous, ask clarifying questions using `AskUserQuestion` before proceeding. Do not guess scope.
 - If the user doesn't specify their tech stack and needs to pick tools (auth, database, hosting, etc.), read `plan/references/stack-defaults.md` for recommended defaults. Suggest them, don't impose them. If the project already has a stack (check package.json, go.mod, requirements.txt), use what's there.
diff --git a/qa/SKILL.md b/qa/SKILL.md
@@ -57,6 +57,14 @@ Use Playwright directly — do not install a custom browser daemon. Use `qa/bin/
 
 After functional tests pass, take screenshots of every key state and analyze the UI visually. This is not optional for web apps. A feature that works but looks broken is broken.
 
+**Read the plan artifact first:**
+
+```bash
+bin/find-artifact.sh plan 2
+```
+
+If the plan specifies product standards (shadcn/ui, Tailwind, dark mode, specific component library), use those as your checklist. Don't guess what the UI should look like. The plan defines the spec. If the plan said "shadcn/ui + Tailwind" and the output uses raw CSS, that's a finding.
+
 **Take screenshots of:**
 - Home/landing page
 - Main feature in empty state (no data)
diff --git a/review/SKILL.md b/review/SKILL.md
@@ -30,7 +30,20 @@ Auto-suggest logic (recommend, don't enforce):
 
 Calibrate depth by diff size: **Small** (< 100 lines, quick pass) / **Medium** (100-500, full two-pass) / **Large** (500+, full + architecture).
 
-## Step 0: Scope Drift Check
+## Step 0: Read Plan Context
+
+Find the plan artifact and extract context for the review:
+
+```bash
+bin/find-artifact.sh plan 2
+```
+
+If found, read these fields:
+- **`planned_files[]`** → used by scope drift check (below)
+- **`risks[]`** → create a risk checklist. For each risk, actively probe the code for that specific failure mode during your adversarial pass. These risks were identified during planning and should be verified.
+- **`out_of_scope[]`** → verify none of these were implemented. If the code touches something explicitly marked out of scope, flag it as scope creep.
+
+## Step 0.5: Scope Drift Check
 
 Always run if a recent plan artifact exists. In `--quick` mode, drift is informational. In `--standard`, drift is informational. In `--thorough`, drift is BLOCKING.
 
diff --git a/security/SKILL.md b/security/SKILL.md
@@ -27,7 +27,17 @@ Auto-suggest:
 
 ## Setup (first run per project)
 
-First read project config: `bin/init-config.sh`. Use `detected` to scope which checks to run (skip Python checks in a Go project). Use `preferences.conflict_precedence` for cross-skill conflicts.
+**Read the plan artifact** if one exists:
+
+```bash
+bin/find-artifact.sh plan 2
+```
+
+If found:
+- **`planned_files[]`** → focus your audit on these files and their dependencies. Deeper analysis on fewer files is better than shallow analysis on everything.
+- **`risks[]`** → treat each planned risk as a security hypothesis to verify. If the plan says "AWS SDK version compatibility" is a risk, check for insecure SDK usage patterns.
+
+Then read project config: `bin/init-config.sh`. Use `detected` to scope which checks to run (skip Python checks in a Go project). Use `preferences.conflict_precedence` for cross-skill conflicts.
 
 Then check if `security/config.json` exists. If not, ask the user to classify the project:
 
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -24,6 +24,14 @@ ship/bin/quality-check.sh     # broken README links, stale references, writing q
 
 If either reports errors, fix them before proceeding. Warnings are informational but should be reviewed.
 
+**Verify review findings were resolved:**
+
+```bash
+bin/find-artifact.sh review 2
+```
+
+If a review artifact exists, check that all **blocking** findings have been addressed. For each blocking finding, verify the code at the reported file and line no longer has the issue. If a blocking finding is still present, do NOT proceed. Flag it.
+
 Then verify:
 
 ```bash
PATCH

echo "Gold patch applied."
