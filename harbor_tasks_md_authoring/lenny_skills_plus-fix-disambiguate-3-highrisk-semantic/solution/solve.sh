#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lenny-skills-plus

# Idempotency guard
if grep -qF "description: \"Lead ongoing cross-functional collaboration by producing a Cross-F" "skills/cross-functional-collaboration/SKILL.md" && grep -qF "description: \"Evaluate trade-offs and produce a Trade-off Evaluation Pack (trade" "skills/evaluating-trade-offs/SKILL.md" && grep -qF "description: \"Manage up effectively and produce a Managing Up Operating System P" "skills/managing-up/SKILL.md" && grep -qF "description: \"Run a high-quality decision process and produce a Decision Process" "skills/running-decision-processes/SKILL.md" && grep -qF "description: \"Align stakeholders and secure buy-in for a specific proposal or de" "skills/stakeholder-alignment/SKILL.md" && grep -qF "description: \"Apply systems thinking to leadership decisions and produce a Syste" "skills/systems-thinking/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/cross-functional-collaboration/SKILL.md b/skills/cross-functional-collaboration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "cross-functional-collaboration"
-description: "Lead cross-functional collaboration by producing a Cross-Functional Collaboration Pack (mission charter, stakeholder/incentives map, roles & expectations contract, operating cadence, decision log, conflict + credit norms). Use for cross-functional collaboration, working with engineering, working with design, reducing execution friction. Category: Leadership."
+description: "Lead ongoing cross-functional collaboration by producing a Cross-Functional Collaboration Pack (mission charter, stakeholder/incentives map, roles & expectations contract, operating cadence, decision log, conflict + credit norms). Use for cross-functional collaboration, working with engineering, working with design, and reducing execution friction. NOT for one-time stakeholder buy-in (use stakeholder-alignment) or managing your boss (use managing-up). Category: Leadership."
 ---
 
 # Cross-functional Collaboration
diff --git a/skills/evaluating-trade-offs/SKILL.md b/skills/evaluating-trade-offs/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "evaluating-trade-offs"
-description: "Evaluate trade-offs and produce a Trade-off Evaluation Pack (trade-off brief, options+criteria matrix, all-in cost/opportunity cost table, impact ranges, recommendation, stop/continue triggers). Use for tradeoff/trade-off, pros and cons, cost-benefit, opportunity cost, build vs buy, ship fast vs ship better, continue vs stop (sunk costs). Category: Leadership."
+description: "Evaluate trade-offs and produce a Trade-off Evaluation Pack (trade-off brief, options+criteria matrix, all-in cost/opportunity cost table, impact ranges, recommendation, stop/continue triggers). Use for tradeoff/trade-off, pros and cons, cost-benefit, opportunity cost, ship fast vs ship better, and continue vs stop (sunk costs). NOT for technology/vendor build-vs-buy (use evaluating-new-technology). Category: Leadership."
 ---
 
 # Evaluating Trade-offs
@@ -25,6 +25,7 @@ description: "Evaluate trade-offs and produce a Trade-off Evaluation Pack (trade
 - You need to clarify what problem you’re solving (use `problem-definition`).
 - You need a full cross-functional decision process (use `running-decision-processes`).
 - You’re prioritizing across many initiatives (use `prioritizing-roadmap`).
+- You’re evaluating a specific technology, vendor, or build-vs-buy for a tool/platform (use `evaluating-new-technology`).
 - You’re cutting scope to hit a date/timebox (use `scoping-cutting`).
 - The decision is personal/legal/HR/financial advice (escalate to qualified humans).
 
diff --git a/skills/managing-up/SKILL.md b/skills/managing-up/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "managing-up"
-description: "Manage up effectively and produce a Managing Up Operating System Pack (manager profile, comms cadence, weekly updates, escalation/ask plan, expectation & boundary script, and exec-ready decision/tradeoff memo). Use for managing up, managing your boss, working with your manager, exec communication, stakeholder updates, and escalation. Category: Leadership."
+description: "Manage up effectively and produce a Managing Up Operating System Pack (manager profile, comms cadence, weekly updates, escalation/ask plan, expectation & boundary script, and exec-ready decision/tradeoff memo). Use for managing up, managing your boss, working with your manager, exec communication, and escalation. NOT for broad stakeholder buy-in (use stakeholder-alignment) or cross-team collaboration setup (use cross-functional-collaboration). Category: Leadership."
 ---
 
 # Managing Up
diff --git a/skills/running-decision-processes/SKILL.md b/skills/running-decision-processes/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "running-decision-processes"
-description: "Run a high-quality decision process and produce a Decision Process Pack (decision brief/pre-read, options + criteria matrix, RAPID/DACI roles, decision meeting plan, decision log entry, comms, review plan). Use for decision making, decision memo, decision log, one-way door vs two-way door, RAPID, DACI, RACI, exec alignment. Category: Leadership."
+description: "Run a high-quality decision process and produce a Decision Process Pack (decision brief/pre-read, options + criteria matrix, RAPID/DACI roles, decision meeting plan, decision log entry, comms, review plan). Use for decision making, decision memo, decision log, one-way door vs two-way door, RAPID, DACI, RACI, and exec decision alignment. NOT for analytical trade-off comparison (use evaluating-trade-offs) or systemic second-order effects analysis (use systems-thinking). Category: Leadership."
 ---
 
 # Running Decision Processes
diff --git a/skills/stakeholder-alignment/SKILL.md b/skills/stakeholder-alignment/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "stakeholder-alignment"
-description: "Align stakeholders and secure buy-in by producing a Stakeholder Alignment Pack (alignment brief, stakeholder map, exec decision principles, pre-brief plan, alignment meeting plan, decision summary + comms). Use for stakeholder alignment, buy-in, executive alignment, cross-functional alignment. Category: Communication."
+description: "Align stakeholders and secure buy-in for a specific proposal or decision by producing a Stakeholder Alignment Pack (alignment brief, stakeholder map, exec decision principles, pre-brief plan, alignment meeting plan, decision summary + comms). Use for stakeholder alignment, buy-in, executive alignment, and securing approval. NOT for ongoing cross-functional collaboration (use cross-functional-collaboration) or managing your boss relationship (use managing-up). Category: Communication."
 ---
 
 # Stakeholder Alignment
diff --git a/skills/systems-thinking/SKILL.md b/skills/systems-thinking/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "systems-thinking"
-description: "Apply systems thinking to leadership decisions and produce a Systems Thinking Pack (system boundary, actors & incentives map, feedback loops, second-order effects ledger, leverage points, intervention plan). Use for complex ecosystems, trade-offs, org/process redesign, and preventing unintended consequences. Category: Leadership."
+description: "Apply systems thinking to leadership decisions and produce a Systems Thinking Pack (system boundary, actors & incentives map, feedback loops, second-order effects ledger, leverage points, intervention plan). Use for complex ecosystems, second-order effects, feedback loops, org/process redesign, and preventing unintended consequences. NOT for single-decision trade-off analysis (use evaluating-trade-offs) or decision process facilitation (use running-decision-processes). Category: Leadership."
 ---
 
 # Systems Thinking
PATCH

echo "Gold patch applied."
