#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superpowers

# Idempotency guard
if grep -qF "The failure mode is not \"too little ceremony.\" It is jumping to implementation w" "skills/brainstorming/SKILL.md" && grep -qF "Scale the review process to the task. A one-line config change doesn't need the " "skills/subagent-driven-development/SKILL.md" && grep -qF "**GATE \u2014 Do not elide without permission.** For small, single-file changes, the " "skills/writing-plans/SKILL.md" && grep -qF "- **Behavioral gates** \u2014 decision diamonds in process flows act as enforcement m" "skills/writing-skills/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/brainstorming/SKILL.md b/skills/brainstorming/SKILL.md
@@ -1,58 +1,76 @@
 ---
 name: brainstorming
-description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
+description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior."
 ---
 
 # Brainstorming Ideas Into Designs
 
-Help turn ideas into fully formed designs and specs through natural collaborative dialogue.
+## Overview
+
+Help turn ideas into fully formed designs and specs through natural collaborative dialogue. Scale your effort to the task — a link in a header needs a different process than a new subsystem — but always confirm you understand what the user wants before you build anything.
 
 Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.
 
 <HARD-GATE>
-Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
+Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until:
+1. You have stated your understanding of the user's intent
+2. The user has confirmed that understanding
+
+This applies to every task regardless of size. The confirmation can be brief ("I'll add a GitHub icon-link to the header, styled to match the existing theme — sound right?"), but you must get it.
 </HARD-GATE>
 
-## Anti-Pattern: "This Is Too Simple To Need A Design"
+## Anti-Pattern: Skipping Understanding
 
-Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.
+The failure mode is not "too little ceremony." It is jumping to implementation with unchecked assumptions. Simple tasks are where this happens most — you assume you know what the user wants and start editing. Even when you're right about the *what*, you miss preferences about the *how*.
 
 ## Checklist
 
-You MUST create a task for each of these items and complete them in order:
+Create tasks to track the steps you'll execute. For a small change, that might be steps 1–3 only. For a large project, all seven.
 
 1. **Explore project context** — check files, docs, recent commits
 2. **Offer visual companion** (if topic will involve visual questions) — this is its own message, not combined with a clarifying question. See the Visual Companion section below.
 3. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
-4. **Propose 2-3 approaches** — with trade-offs and your recommendation
+4. **Propose approaches** — with trade-offs and your recommendation
 5. **Present design** — in sections scaled to their complexity, get user approval after each section
-6. **Write design doc** — save to `docs/plans/YYYY-MM-DD-<topic>-design.md` and commit
+6. **Write design doc** — save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and commit
 7. **Transition to implementation** — invoke writing-plans skill to create implementation plan
 
+Steps 1–4 always happen. Steps 5–7 scale to the task. **GATE — when you believe a step can be safely elided, ask the user for permission.** Do not skip silently. For example: "This is straightforward — I don't think we need a design doc. Want me to go straight to planning?"
+
 ## Process Flow
 
 ```dot
 digraph brainstorming {
-    "Explore project context" [shape=box];
-    "Visual questions ahead?" [shape=diamond];
-    "Offer Visual Companion\n(own message, no other content)" [shape=box];
-    "Ask clarifying questions" [shape=box];
-    "Propose 2-3 approaches" [shape=box];
-    "Present design sections" [shape=box];
-    "User approves design?" [shape=diamond];
+    "Explore context" [shape=box];
+    "Visual questions?" [shape=diamond];
+    "Offer Visual Companion" [shape=box];
+    "Understand intent" [shape=box];
+    "User confirms understanding?" [shape=diamond];
+    "Propose approaches" [shape=box];
+    "Present design" [shape=box];
+    "User approves?" [shape=diamond];
+    "Design doc warranted?" [shape=diamond];
+    "Ask user permission\nto elide" [shape=box];
     "Write design doc" [shape=box];
-    "Invoke writing-plans skill" [shape=doublecircle];
-
-    "Explore project context" -> "Visual questions ahead?";
-    "Visual questions ahead?" -> "Offer Visual Companion\n(own message, no other content)" [label="yes"];
-    "Visual questions ahead?" -> "Ask clarifying questions" [label="no"];
-    "Offer Visual Companion\n(own message, no other content)" -> "Ask clarifying questions";
-    "Ask clarifying questions" -> "Propose 2-3 approaches";
-    "Propose 2-3 approaches" -> "Present design sections";
-    "Present design sections" -> "User approves design?";
-    "User approves design?" -> "Present design sections" [label="no, revise"];
-    "User approves design?" -> "Write design doc" [label="yes"];
-    "Write design doc" -> "Invoke writing-plans skill";
+    "Spec review\n(when warranted)" [shape=box];
+    "Invoke writing-plans" [shape=doublecircle];
+
+    "Explore context" -> "Visual questions?";
+    "Visual questions?" -> "Offer Visual Companion" [label="yes"];
+    "Visual questions?" -> "Understand intent" [label="no"];
+    "Offer Visual Companion" -> "Understand intent";
+    "Understand intent" -> "User confirms understanding?";
+    "User confirms understanding?" -> "Understand intent" [label="no, refine"];
+    "User confirms understanding?" -> "Propose approaches" [label="yes"];
+    "Propose approaches" -> "Present design";
+    "Present design" -> "User approves?";
+    "User approves?" -> "Present design" [label="no, revise"];
+    "User approves?" -> "Design doc warranted?" [label="yes"];
+    "Design doc warranted?" -> "Write design doc" [label="yes"];
+    "Design doc warranted?" -> "Ask user permission\nto elide" [label="no — may be\noverkill"];
+    "Ask user permission\nto elide" -> "Invoke writing-plans";
+    "Write design doc" -> "Spec review\n(when warranted)";
+    "Spec review\n(when warranted)" -> "Invoke writing-plans";
 }
 ```
 
@@ -84,48 +102,52 @@ digraph brainstorming {
 - Cover: architecture, components, data flow, error handling, testing
 - Be ready to go back and clarify if something doesn't make sense
 
-**Design for isolation and clarity:**
-
-- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
-- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
-- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
-- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.
-
-**Working in existing codebases:**
-
-- Explore the current structure before proposing changes. Follow existing patterns.
-- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
-- Don't propose unrelated refactoring. Stay focused on what serves the current goal.
-
 ## After the Design
 
-**Documentation:**
+**Documentation (when warranted):**
 
 - Write the validated design (spec) to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
   - (User preferences for spec location override this default)
 - Use elements-of-style:writing-clearly-and-concisely skill if available
 - Commit the design document to git
+- **GATE — for small changes, the design doc may be unnecessary.** Ask the user before skipping it.
 
-**Spec Review Loop:**
+**Spec Review Loop (when warranted):**
 After writing the spec document:
 
 1. Dispatch spec-document-reviewer subagent (see spec-document-reviewer-prompt.md)
 2. If Issues Found: fix, re-dispatch, repeat until Approved
 3. If loop exceeds 5 iterations, surface to human for guidance
 
+**GATE — for small changes, the spec review may be unnecessary.** Ask the user before skipping it.
+
 **Implementation:**
 
-- Invoke the writing-plans skill to create a detailed implementation plan
+- Check in with the user before transitioning: "The design is ready. Want me to move on to writing the implementation plan?"
+- On confirmation, invoke the writing-plans skill
 - Do NOT invoke any other skill. writing-plans is the next step.
 
+**Design for isolation and clarity:**
+
+- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
+- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
+- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
+- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.
+
+**Working in existing codebases:**
+
+- Explore the current structure before proposing changes. Follow existing patterns.
+- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
+- Don't propose unrelated refactoring. Stay focused on what serves the current goal.
+
 ## Key Principles
 
-- **One question at a time** - Don't overwhelm with multiple questions
-- **Multiple choice preferred** - Easier to answer than open-ended when possible
-- **YAGNI ruthlessly** - Remove unnecessary features from all designs
-- **Explore alternatives** - Always propose 2-3 approaches before settling
-- **Incremental validation** - Present design, get approval before moving on
-- **Be flexible** - Go back and clarify when something doesn't make sense
+- **One question at a time** — don't overwhelm with multiple questions
+- **Multiple choice preferred** — easier to answer than open-ended when possible
+- **YAGNI ruthlessly** — remove unnecessary features from all designs
+- **Explore alternatives** — propose approaches before settling
+- **Incremental validation** — present, get approval, then move on
+- **Be flexible** — go back and clarify when something doesn't make sense
 
 ## Visual Companion
 
diff --git a/skills/subagent-driven-development/SKILL.md b/skills/subagent-driven-development/SKILL.md
@@ -7,6 +7,8 @@ description: Use when executing implementation plans with independent tasks in t
 
 Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.
 
+Scale the review process to the task. A one-line config change doesn't need the same review rigor as a new subsystem. **GATE — when you believe review stages or the final reviewer can be safely collapsed or elided, ask the user for permission.** Do not elide silently, and do not replace a skipped review subagent with orchestrator judgment — the orchestrator never implements or reviews code.
+
 **Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration
 
 ## When to Use
@@ -47,38 +49,50 @@ digraph process {
         "Implementer subagent asks questions?" [shape=diamond];
         "Answer questions, provide context" [shape=box];
         "Implementer subagent implements, tests, commits, self-reviews" [shape=box];
+        "Two-stage review warranted?" [shape=diamond];
+        "Ask user permission\nto elide or collapse reviews" [shape=box];
         "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" [shape=box];
         "Spec reviewer subagent confirms code matches spec?" [shape=diamond];
         "Implementer subagent fixes spec gaps" [shape=box];
         "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" [shape=box];
         "Code quality reviewer subagent approves?" [shape=diamond];
         "Implementer subagent fixes quality issues" [shape=box];
-        "Mark task complete in TodoWrite" [shape=box];
+        "Mark task complete in your task list" [shape=box];
     }
 
-    "Read plan, extract all tasks with full text, note context, create TodoWrite" [shape=box];
+    "Read plan, extract all tasks with full text, note context, create your task list" [shape=box];
     "More tasks remain?" [shape=diamond];
+    "Final reviewer warranted?" [shape=diamond];
+    "Ask user permission\nto elide final review" [shape=box];
     "Dispatch final code reviewer subagent for entire implementation" [shape=box];
+    "Check in with user\nbefore finishing" [shape=box];
     "Use superpowers:finishing-a-development-branch" [shape=box style=filled fillcolor=lightgreen];
 
-    "Read plan, extract all tasks with full text, note context, create TodoWrite" -> "Dispatch implementer subagent (./implementer-prompt.md)";
+    "Read plan, extract all tasks with full text, note context, create your task list" -> "Dispatch implementer subagent (./implementer-prompt.md)";
     "Dispatch implementer subagent (./implementer-prompt.md)" -> "Implementer subagent asks questions?";
     "Implementer subagent asks questions?" -> "Answer questions, provide context" [label="yes"];
     "Answer questions, provide context" -> "Dispatch implementer subagent (./implementer-prompt.md)";
     "Implementer subagent asks questions?" -> "Implementer subagent implements, tests, commits, self-reviews" [label="no"];
-    "Implementer subagent implements, tests, commits, self-reviews" -> "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)";
+    "Implementer subagent implements, tests, commits, self-reviews" -> "Two-stage review warranted?";
+    "Two-stage review warranted?" -> "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" [label="yes"];
+    "Two-stage review warranted?" -> "Ask user permission\nto elide or collapse reviews" [label="no — may be\noverkill"];
+    "Ask user permission\nto elide or collapse reviews" -> "Mark task complete in your task list";
     "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" -> "Spec reviewer subagent confirms code matches spec?";
     "Spec reviewer subagent confirms code matches spec?" -> "Implementer subagent fixes spec gaps" [label="no"];
     "Implementer subagent fixes spec gaps" -> "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" [label="re-review"];
     "Spec reviewer subagent confirms code matches spec?" -> "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" [label="yes"];
     "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" -> "Code quality reviewer subagent approves?";
     "Code quality reviewer subagent approves?" -> "Implementer subagent fixes quality issues" [label="no"];
     "Implementer subagent fixes quality issues" -> "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" [label="re-review"];
-    "Code quality reviewer subagent approves?" -> "Mark task complete in TodoWrite" [label="yes"];
-    "Mark task complete in TodoWrite" -> "More tasks remain?";
+    "Code quality reviewer subagent approves?" -> "Mark task complete in your task list" [label="yes"];
+    "Mark task complete in your task list" -> "More tasks remain?";
     "More tasks remain?" -> "Dispatch implementer subagent (./implementer-prompt.md)" [label="yes"];
-    "More tasks remain?" -> "Dispatch final code reviewer subagent for entire implementation" [label="no"];
-    "Dispatch final code reviewer subagent for entire implementation" -> "Use superpowers:finishing-a-development-branch";
+    "More tasks remain?" -> "Final reviewer warranted?" [label="no"];
+    "Final reviewer warranted?" -> "Dispatch final code reviewer subagent for entire implementation" [label="yes"];
+    "Final reviewer warranted?" -> "Ask user permission\nto elide final review" [label="no — may be\noverkill"];
+    "Ask user permission\nto elide final review" -> "Check in with user\nbefore finishing";
+    "Dispatch final code reviewer subagent for entire implementation" -> "Check in with user\nbefore finishing";
+    "Check in with user\nbefore finishing" -> "Use superpowers:finishing-a-development-branch";
 }
 ```
 
@@ -128,7 +142,7 @@ You: I'm using Subagent-Driven Development to execute this plan.
 
 [Read plan file once: docs/superpowers/plans/feature-plan.md]
 [Extract all 5 tasks with full text and context]
-[Create TodoWrite with all tasks]
+[Create your task list with all tasks]
 
 Task 1: Hook installation script
 
@@ -233,7 +247,7 @@ Done!
 
 **Never:**
 - Start implementation on main/master branch without explicit user consent
-- Skip reviews (spec compliance OR code quality)
+- Skip any review without explicit user permission
 - Proceed with unfixed issues
 - Dispatch multiple implementation subagents in parallel (conflicts)
 - Make subagent read plan file (provide full text instead)
@@ -258,7 +272,7 @@ Done!
 
 **If subagent fails task:**
 - Dispatch fix subagent with specific instructions
-- Don't try to fix manually (context pollution)
+- Don't try to fix manually — the orchestrator never implements or reviews code (context pollution)
 
 ## Integration
 
diff --git a/skills/writing-plans/SKILL.md b/skills/writing-plans/SKILL.md
@@ -7,6 +7,8 @@ description: Use when you have a spec or requirements for a multi-step task, bef
 
 ## Overview
 
+Scale the plan to the task. A one-file change doesn't need the same plan as a new subsystem. When you believe steps can be safely elided, ask the user for permission — don't elide silently, and don't follow the full process rigidly when it doesn't serve the work.
+
 Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.
 
 Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.
@@ -110,8 +112,39 @@ git commit -m "feat: add specific feature"
 - Reference relevant skills with @ syntax
 - DRY, YAGNI, TDD, frequent commits
 
+## Process Flow
+
+```dot
+digraph writing_plans {
+    rankdir=TB;
+    node [shape=box];
+
+    announce [label="Announce skill usage"];
+    scope [label="Scope check"];
+    file_structure [label="Map file structure"];
+    write_tasks [label="Write bite-sized tasks\n(header, task structure, code)"];
+    review_needed [label="Review loop warranted?" shape=diamond];
+    ask_user [label="Ask user permission\nto elide review loop" shape=box];
+    user_says [label="User approves\neliding?" shape=diamond];
+    review_loop [label="Dispatch plan-document-reviewer\nper chunk; fix until ✅"];
+    save_plan [label="Save plan to\ndocs/superpowers/plans/"];
+    handoff [label="Execution handoff:\n\"Ready to execute?\""];
+
+    announce -> scope -> file_structure -> write_tasks -> review_needed;
+    review_needed -> review_loop [label="yes"];
+    review_needed -> ask_user [label="no — may be\noverkill"];
+    ask_user -> user_says;
+    user_says -> review_loop [label="no, do the review"];
+    user_says -> save_plan [label="yes, elide it"];
+    review_loop -> save_plan;
+    save_plan -> handoff;
+}
+```
+
 ## Plan Review Loop
 
+**GATE — Do not elide without permission.** For small, single-file changes, the review loop may be unnecessary. If you believe it can be safely elided, you MUST ask the user before proceeding without it. Do not silently skip the review loop. Do not treat this as optional. Present your reasoning and wait for the user's answer.
+
 After completing each chunk of the plan:
 
 1. Dispatch plan-document-reviewer subagent (see plan-document-reviewer-prompt.md) for the current chunk
@@ -133,15 +166,19 @@ After completing each chunk of the plan:
 
 After saving the plan:
 
-**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Ready to execute?"**
+**1. Record context.** Before anything else, verify all artifacts are saved and the plan is self-contained:
+- Spec document path (if one was written)
+- Plan document path
+- Key architectural decisions, constraints, or user preferences that affect implementation but aren't captured in the plan — add them to the plan now
+
+**2. Advise compaction.** Execution works better with a fresh window. Tell the user:
+
+> "The plan is saved to `docs/superpowers/plans/<filename>.md`. Before we start implementation, I recommend compacting this session — execution works better with a fresh window."
+
+**3. Give exact continuation prompt.** Tell the user exactly what to say after compacting. Use the actual filename, not a placeholder.
 
-**Execution path depends on harness capabilities:**
+If you can dispatch subagents (Claude Code, etc.):
 
-**If harness has subagents (Claude Code, etc.):**
-- **REQUIRED:** Use superpowers:subagent-driven-development
-- Do NOT offer a choice - subagent-driven is the standard approach
-- Fresh subagent per task + two-stage review
+> "After compacting, say: **Execute the plan at `docs/superpowers/plans/<filename>.md` using subagent-driven-development.**"
 
-**If harness does NOT have subagents:**
-- Execute plan in current session using superpowers:executing-plans
-- Batch execution with checkpoints for review
+If you cannot dispatch subagents, ask the user: "The plan is ready. I can't dispatch subagents in this environment — should I execute the tasks in this thread?"
diff --git a/skills/writing-skills/SKILL.md b/skills/writing-skills/SKILL.md
@@ -306,6 +306,7 @@ digraph when_flowchart {
 - Non-obvious decision points
 - Process loops where you might stop too early
 - "When to use A vs B" decisions
+- **Behavioral gates** — decision diamonds in process flows act as enforcement mechanisms, not just documentation. Testing showed agents follow graphviz gates more reliably than prose instructions alone (writing-plans: 2/5 → 5/5 compliance after adding a process diagram with a gate diamond).
 
 **Never use flowcharts for:**
 - Reference material → Tables, lists
@@ -484,6 +485,18 @@ Write code before test? Delete it. Start over.
 ```
 </Good>
 
+### Use GATE Markers for Non-Optional Decision Points
+
+Label decision points that must not be silently bypassed with `**GATE —**` followed by the constraint:
+
+```markdown
+**GATE — Do not elide without permission.** If you believe
+the review loop can be safely skipped, you MUST ask the user
+before proceeding. Present your reasoning and wait for their answer.
+```
+
+Agents treat GATE-marked instructions as harder constraints than unmarked prose. Pair with a decision diamond in the process flow diagram for strongest effect.
+
 ### Address "Spirit vs Letter" Arguments
 
 Add foundational principle early:
PATCH

echo "Gold patch applied."
