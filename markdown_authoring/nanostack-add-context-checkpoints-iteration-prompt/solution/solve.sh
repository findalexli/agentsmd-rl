#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "bin/save-artifact.sh compound '<json with phase, summary including solutions_cre" "compound/SKILL.md" && grep -qF "After build completes, run `/review`, `/security` and `/qa` **in parallel** usin" "plan/SKILL.md" && grep -qF "**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifac" "qa/SKILL.md" && grep -qF "**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to th" "review/SKILL.md" && grep -qF "**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifac" "security/SKILL.md" && grep -qF "**2. What could come next.** Suggest 2-3 concrete extensions based on what was b" "ship/SKILL.md" && grep -qF "bin/save-artifact.sh think '<json with phase, summary including value_propositio" "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/compound/SKILL.md b/compound/SKILL.md
@@ -127,9 +127,11 @@ Total solutions in project: 12
 ## Save Artifact
 
 ```bash
-bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions>'
+bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
+The `context_checkpoint` is mandatory. Summarize how many solutions were created/updated and their types.
+
 ## Next Step
 
 > Knowledge captured. These solutions will be found automatically by /nano during planning and /review during code review.
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -131,9 +131,11 @@ Present the plan to the user. Wait for explicit approval before executing. If th
 Always persist the plan after presenting it to the user:
 
 ```bash
-bin/save-artifact.sh plan '<json with phase, summary including planned_files array>'
+bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
+The `context_checkpoint` is mandatory. Summarize the plan scope, list planned files, and document key decisions (e.g., "small scope, 2 files" or "chose X over Y because Z").
+
 The `planned_files` list is critical. `/review` uses it for scope drift detection via `bin/scope-drift.sh`. See `reference/artifact-schema.md` for the full schema.
 
 The user can disable auto-saving by setting `auto_save: false` in `.nanostack/config.json`.
@@ -144,16 +146,27 @@ After the user approves the plan and you finish building:
 
 **If AUTOPILOT is active:**
 
-Proceed directly to `/review`. After review completes, run `/security`. After security, run `/qa`. After all three pass, run `/ship`. Only stop if:
-- `/review` finds **blocking** issues that need user decision
-- `/security` finds **critical** vulnerabilities
-- A product question comes up that you can't answer from context
+After build completes, run `/review`, `/security` and `/qa` **in parallel** using three Agent tool calls in a single message. These three phases are all read-only (they analyze code but don't modify it) and have no dependencies on each other.
+
+```
+Launch 3 agents in parallel (single message, 3 Agent tool calls):
+
+Agent 1: "Run /review on this project. Save the artifact when done. Return the summary."
+Agent 2: "Run /security on this project. Save the artifact when done. Return the summary."
+Agent 3: "Run /qa on this project. Save the artifact when done. Return the summary."
+```
+
+Show status as results come back:
+> Autopilot: running /review, /security and /qa in parallel...
+> Autopilot: review complete (X findings, 0 blocking).
+> Autopilot: security grade A (0 critical, 0 high).
+> Autopilot: qa passed (X tests, 0 failed).
+
+After all three complete, check results:
+- If any has **blocking issues**, **critical vulnerabilities**, or **test failures**: stop and ask the user
+- If all three pass: proceed to `/ship`
 
-Between each step, show a brief status:
-> Autopilot: build complete. Running /review...
-> Autopilot: review clean. Running /security...
-> Autopilot: security grade A. Running /qa...
-> Autopilot: qa passed. Running /ship...
+If parallel execution is not available (single-threaded agent, no Agent tool), fall back to running them sequentially: `/review` → `/security` → `/qa`.
 
 **Otherwise (default):**
 
diff --git a/qa/SKILL.md b/qa/SKILL.md
@@ -196,9 +196,11 @@ Report progress as you go. After each test group (happy path, error states, edge
 Always persist the QA results after completing the run:
 
 ```bash
-bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings>'
+bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
+The `context_checkpoint` is mandatory. Summarize tests passed/failed, bugs found/fixed, and WTF likelihood.
+
 See `reference/artifact-schema.md` for the full schema. The user can disable auto-saving by setting `auto_save: false` in `.nanostack/config.json`.
 
 ## Mode Summary
@@ -216,9 +218,11 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 
 After QA is complete and the artifact is saved:
 
-**If AUTOPILOT is active and tests pass:** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`
+**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.
+
+**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`
 
-**If AUTOPILOT is active but tests fail:** Stop and ask the user. Show failures and wait.
+**If AUTOPILOT is active but tests fail:** Return the failures. The parent agent (or sequential flow) will stop and ask the user.
 
 **Otherwise:** Tell the user:
 > QA complete. Remaining steps:
diff --git a/review/SKILL.md b/review/SKILL.md
@@ -133,9 +133,11 @@ When a conflict is detected, mark it inline:
 Always persist the review after completing it:
 
 ```bash
-bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts>'
+bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
+The `context_checkpoint` is mandatory. Summarize findings count and severity, scope drift status, and any auto-fixes applied.
+
 See `reference/artifact-schema.md` for the full schema. The user can disable auto-saving by setting `auto_save: false` in `.nanostack/config.json`.
 
 ## Mode Summary
@@ -152,9 +154,11 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 
 After the review is complete and the artifact is saved:
 
-**If AUTOPILOT is active and no blocking issues found:** Proceed directly to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /security...`
+**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.
+
+**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /security...`
 
-**If AUTOPILOT is active but blocking issues found:** Stop and ask the user to resolve. Show the blocking issues and wait. After resolution, continue autopilot.
+**If AUTOPILOT is active but blocking issues found:** Return the blocking issues. The parent agent (or sequential flow) will stop and ask the user.
 
 **Otherwise:** Tell the user:
 > Review complete. Remaining steps:
diff --git a/security/SKILL.md b/security/SKILL.md
@@ -224,9 +224,11 @@ In `--thorough` mode, document conflicts AND flag as BLOCKING until user confirm
 Always persist the security audit after completing it:
 
 ```bash
-bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts>'
+bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
+The `context_checkpoint` is mandatory. Summarize the security grade, finding counts by severity, and any critical decisions.
+
 See `reference/artifact-schema.md` for the full schema. The user can disable auto-saving by setting `auto_save: false` in `.nanostack/config.json`.
 
 ## Mode Summary
@@ -244,9 +246,11 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 
 After the security audit is complete and the artifact is saved:
 
-**If AUTOPILOT is active and no critical/high findings:** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`
+**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.
+
+**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`
 
-**If AUTOPILOT is active but critical or high findings found:** Stop and ask the user to review. Show the findings and wait. After resolution, continue autopilot.
+**If AUTOPILOT is active but critical or high findings found:** Return the findings. The parent agent (or sequential flow) will stop and ask the user.
 
 **Otherwise:** Tell the user:
 > Security audit complete. Remaining steps:
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -186,10 +186,22 @@ Before creating the PR, verify these standards. The public repo is the face of t
 After shipping, persist the result and generate the sprint journal:
 
 ```bash
-bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed>'
+bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 bin/sprint-journal.sh
 ```
 
+The `context_checkpoint` is mandatory. Summarize what was shipped, PR number, and CI status.
+
+### Show the result
+
+After shipping, if the project produces a viewable output (HTML file, web app, CLI tool), tell the user how to see it:
+
+- HTML files: "Open `index.html` in your browser to see the result"
+- Web apps: "Run `npm start` and open http://localhost:3000"
+- CLI tools: "Run `node bin/cli.js --help` to try it"
+
+Never auto-open URLs or execute `open` commands. Show the path or command and let the user decide.
+
 The sprint journal reads all phase artifacts (think, plan, review, qa, security, ship) and writes a single entry to `.nanostack/know-how/journal/`. This happens automatically on every successful ship.
 
 The user can disable auto-saving by setting `auto_save: false` in `.nanostack/config.json`.
@@ -226,10 +238,19 @@ These were discovered from shipping real PRs:
 
 ## Next Step
 
-After shipping, the sprint is complete. Tell the user:
+After shipping, close with two things: what was built and what could come next.
+
+**1. What was built.** Summarize what the user now has in plain language. Not phase names or artifact counts. What does the thing DO, where is it, and how to use it.
+
+**2. What could come next.** Suggest 2-3 concrete extensions based on what was built. These should be things the user can say right now to start a new sprint. Frame them as natural next steps, not feature requests.
+
+Example:
 
-> Sprint complete. PR created. Journal generated at .nanostack/know-how/journal/.
+> Sprint complete. You have a world clock widget showing Buenos Aires, New York and Tokyo with live updates. Open `index.html` in your browser to see it.
 >
-> Run `/compound` to document what you learned. Past solutions are found automatically by /nano and /review in future sprints.
+> Ideas for the next sprint:
+> - "Add a city picker so I can swap timezones"
+> - "Show the date and day of the week under each clock"
+> - "Add a dark/light mode toggle"
 >
-> Run `bin/analytics.sh` to see trends across sprints.
+> Just describe what you want and run `/think` to start a new sprint. Run `/compound` to save what you learned from this one.
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -159,9 +159,11 @@ Ready for: /nano
 Always persist the think output after the handoff brief:
 
 ```bash
-bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated>'
+bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
+The `context_checkpoint` is mandatory. It captures the essence of this phase so downstream phases can restore context without replaying the full conversation. Write a 1-2 sentence summary, list key files, and document decisions made.
+
 See `reference/artifact-schema.md` for the full schema. The user can disable auto-saving by setting `auto_save: false` in `.nanostack/config.json`.
 
 ## Next Step
PATCH

echo "Gold patch applied."
