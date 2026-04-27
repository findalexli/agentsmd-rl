#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "Analyze AI-assisted coding sessions in `~/.gemini/antigravity/brain/` and produc" "skills/analyze-project/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/analyze-project/SKILL.md b/skills/analyze-project/SKILL.md
@@ -7,99 +7,109 @@ tags: [analysis, diagnostics, meta, root-cause, project-health, session-review]
 
 # /analyze-project — Root Cause Analyst Workflow
 
-Analyze AI-assisted coding sessions in `brain/` and produce a diagnostic report that explains not just **what happened**, but **why it happened**, **who/what caused it**, and **what should change next time**.
+Analyze AI-assisted coding sessions in `~/.gemini/antigravity/brain/` and produce a report that explains not just **what happened**, but **why it happened**, **who/what caused it**, and **what should change next time**.
 
-This workflow is not a simple metrics dashboard.
-It is a forensic analysis workflow for AI coding sessions.
-
----
-
-## Primary Objective
+## Goal
 
 For each session, determine:
 
 1. What changed from the initial ask to the final executed work
-2. Whether the change was caused primarily by:
-   - the user/spec
-   - the agent
-   - the codebase/repo
-   - testing/verification
+2. Whether the main cause was:
+   - user/spec
+   - agent
+   - repo/codebase
+   - validation/testing
    - legitimate task complexity
-3. Whether the original prompt was sufficient for the actual job
-4. Which subsystems or files repeatedly correlate with struggle
-5. What concrete changes would most improve future sessions
-
----
+3. Whether the opening prompt was sufficient
+4. Which files/subsystems repeatedly correlate with struggle
+5. What changes would most improve future sessions
 
-## Core Principles
+## Global Rules
 
-- Treat `.resolved.N` counts as **signals of iteration intensity**, not proof of failure
-- Do not label struggle based on counts alone; classify the **shape** of rework
-- Separate **human-added scope** from **necessary discovered scope**
+- Treat `.resolved.N` counts as **iteration signals**, not proof of failure
+- Separate **human-added scope**, **necessary discovered scope**, and **agent-introduced scope**
 - Separate **agent error** from **repo friction**
-- Every diagnosis must include **evidence**
-- Every recommendation must map to a specific observed pattern
-- Use confidence levels:
-  - **High** = directly supported by artifact contents or timestamps
-  - **Medium** = supported by multiple indirect signals
+- Every diagnosis must include **evidence** and **confidence**
+- Confidence levels:
+  - **High** = direct artifact/timestamp evidence
+  - **Medium** = multiple supporting signals
   - **Low** = plausible inference, not directly proven
+- Evidence precedence:
+  - artifact contents > timestamps > metadata summaries > inference
+- If evidence is weak, say so
+
+---
+
+## Step 0.5: Session Intent Classification
+
+Classify the primary session intent from objective + artifacts:
+
+- `DELIVERY`
+- `DEBUGGING`
+- `REFACTOR`
+- `RESEARCH`
+- `EXPLORATION`
+- `AUDIT_ANALYSIS`
+
+Record:
+- `session_intent`
+- `session_intent_confidence`
+
+Use intent to contextualize severity and rework shape.
+Do not judge exploratory or research sessions by the same standards as narrow delivery sessions.
 
 ---
 
-## Step 1: Discovery — Find Relevant Conversations
+## Step 1: Discover Conversations
 
-1. Read the conversation summaries available in the system context.
-2. List all subdirectories in:
-   `~/.gemini/antigravity/brain/
-3. Build a **Conversation Index** by cross-referencing summaries with UUID folders.
-4. Record for each conversation:
+1. Read available conversation summaries from system context
+2. List conversation folders in the user’s Antigravity `brain/` directory
+3. Build a conversation index with:
    - `conversation_id`
    - `title`
    - `objective`
    - `created`
    - `last_modified`
-5. If the user supplied a keyword/path, filter on that. Otherwise analyze all workspace conversations.
+4. If the user supplied a keyword/path, filter to matching conversations; otherwise analyze all
 
-> Output: indexed list of conversations to analyze.
+Output: indexed list of conversations to analyze.
 
 ---
 
-## Step 2: Artifact Extraction — Build Session Evidence
+## Step 2: Extract Session Evidence
 
-For each conversation, read all structured artifacts that exist.
+For each conversation, read if present:
 
-### 2a. Core Artifacts
+### Core artifacts
 - `task.md`
 - `implementation_plan.md`
 - `walkthrough.md`
 
-### 2b. Metadata
+### Metadata
 - `*.metadata.json`
 
-### 2c. Version Snapshots
+### Version snapshots
 - `task.md.resolved.0 ... N`
 - `implementation_plan.md.resolved.0 ... N`
 - `walkthrough.md.resolved.0 ... N`
 
-### 2d. Additional Signals
+### Additional signals
 - other `.md` artifacts
-- report/evaluation files
 - timestamps across artifact updates
-- file/folder names mentioned in plans and walkthroughs
-- repeated subsystem references
-- explicit testing/validation language
-- explicit non-goals or constraints, if present
+- file/folder/subsystem names mentioned in plans/walkthroughs
+- validation/testing language
+- explicit acceptance criteria, constraints, non-goals, and file targets
 
-### 2e. Record Per Conversation
+Record per conversation:
 
-#### Presence / Lifecycle
+#### Lifecycle
 - `has_task`
 - `has_plan`
 - `has_walkthrough`
 - `is_completed`
-- `is_abandoned_candidate` = has task but no walkthrough
+- `is_abandoned_candidate` = task exists but no walkthrough
 
-#### Revision / Change Volume
+#### Revision / change volume
 - `task_versions`
 - `plan_versions`
 - `walkthrough_versions`
@@ -117,7 +127,7 @@ For each conversation, read all structured artifacts that exist.
 - `completed_at`
 - `duration_minutes`
 
-#### Content / Quality Signals
+#### Content / quality
 - `objective_text`
 - `initial_plan_summary`
 - `final_plan_summary`
@@ -134,156 +144,148 @@ For each conversation, read all structured artifacts that exist.
 
 ---
 
-## Step 3: Prompt Sufficiency Analysis
+## Step 3: Prompt Sufficiency
 
-For each conversation, score the opening objective/request on a 0–2 scale for each dimension:
+Score the opening request on a 0–2 scale for:
 
-- **Clarity** — is the ask understandable?
-- **Boundedness** — are scope limits defined?
-- **Testability** — are success conditions or acceptance criteria defined?
-- **Architectural specificity** — are files/modules/systems identified?
-- **Constraint awareness** — are non-goals, constraints, or environment details included?
-- **Dependency awareness** — does the prompt acknowledge affected systems or hidden coupling?
+- **Clarity**
+- **Boundedness**
+- **Testability**
+- **Architectural specificity**
+- **Constraint awareness**
+- **Dependency awareness**
 
 Create:
 - `prompt_sufficiency_score`
 - `prompt_sufficiency_band` = High / Medium / Low
 
-Then note which missing ingredients likely contributed to later friction.
+Then note which missing prompt ingredients likely contributed to later friction.
 
-Important:
-Do not assume a low-detail prompt is bad by default.
-Short prompts can still be good if the task is narrow and the repo context is obvious.
+Do not punish short prompts by default; a narrow, obvious task can still have high sufficiency.
 
 ---
 
 ## Step 4: Scope Change Classification
 
-Do not treat all scope growth as the same.
-
-For each conversation, classify scope delta into:
-
-### 4a. Human-Added Scope
-New items clearly introduced beyond the initial ask.
-Examples:
-- optional enhancements
-- follow-on refactors
-- “while we are here” additions
-- cosmetic or adjacent work added later
+Classify scope change into:
 
-### 4b. Necessary Discovered Scope
-Work that was not in the opening ask but appears required to complete it correctly.
-Examples:
-- dependency fixes
-- required validation work
-- hidden integration tasks
-- migration fallout
-- coupled module updates
+- **Human-added scope** — new asks beyond the original task
+- **Necessary discovered scope** — work required to complete the original task correctly
+- **Agent-introduced scope** — likely unnecessary work introduced by the agent
 
-### 4c. Agent-Introduced Scope
-Work that appears not requested and not necessary, likely introduced by agent overreach.
-
-For each conversation record:
+Record:
 - `scope_change_type_primary`
 - `scope_change_type_secondary` (optional)
 - `scope_change_confidence`
-- evidence for classification
+- evidence
 
----
+Keep one short example in mind for calibration:
+- Human-added: “also refactor nearby code while you’re here”
+- Necessary discovered: hidden dependency must be fixed for original task to work
+- Agent-introduced: extra cleanup or redesign not requested and not required
 
-## Step 5: Rework Shape Analysis
+---
 
-Do not just count revisions. Determine the **shape** of session rework.
+## Step 5: Rework Shape
 
-Classify each conversation into one of these patterns:
+Classify each session into one primary pattern:
 
-- **Clean execution** — little change, smooth completion
-- **Early replan then stable finish** — plan changed early, then execution converged
-- **Progressive scope expansion** — work kept growing throughout the session
-- **Reopen/reclose churn** — repeated task adjustments/backtracking
-- **Late-stage verification churn** — implementation mostly done, but testing/validation caused loops
-- **Abandoned mid-flight** — work started but did not reach walkthrough
-- **Exploratory / research session** — iterations are high but expected due to problem discovery
+- **Clean execution**
+- **Early replan then stable finish**
+- **Progressive scope expansion**
+- **Reopen/reclose churn**
+- **Late-stage verification churn**
+- **Abandoned mid-flight**
+- **Exploratory / research session**
 
 Record:
 - `rework_shape`
 - `rework_shape_confidence`
-- supporting evidence
+- evidence
 
 ---
 
 ## Step 6: Root Cause Analysis
 
 For every non-clean session, assign:
 
-### 6a. Primary Root Cause
-Choose one:
+### Primary root cause
+One of:
 - `SPEC_AMBIGUITY`
 - `HUMAN_SCOPE_CHANGE`
 - `REPO_FRAGILITY`
 - `AGENT_ARCHITECTURAL_ERROR`
 - `VERIFICATION_CHURN`
 - `LEGITIMATE_TASK_COMPLEXITY`
 
-### 6b. Secondary Root Cause
-Optional if a second factor materially contributed.
+### Secondary root cause
+Optional if materially relevant
 
-### 6c. Evidence Requirements
-Every root cause assignment must include:
-- evidence from artifacts or metadata
-- why competing causes were rejected
-- confidence level
+### Root-cause guidance
+- **SPEC_AMBIGUITY**: opening ask lacked boundaries, targets, criteria, or constraints
+- **HUMAN_SCOPE_CHANGE**: scope expanded because the user broadened the task
+- **REPO_FRAGILITY**: hidden coupling, brittle files, unclear architecture, or environment issues forced extra work
+- **AGENT_ARCHITECTURAL_ERROR**: wrong files, wrong assumptions, wrong approach, hallucinated structure
+- **VERIFICATION_CHURN**: implementation mostly worked, but testing/validation caused loops
+- **LEGITIMATE_TASK_COMPLEXITY**: revisions were expected for the difficulty and not clearly avoidable
 
-### 6d. Root Cause Heuristics
+Every root-cause assignment must include:
+- evidence
+- why stronger alternative causes were rejected
+- confidence
+
+---
 
-#### SPEC_AMBIGUITY
-Use when the opening ask lacked boundaries, targets, criteria, or constraints, and the plan had to invent them.
+## Step 6.5: Session Severity Scoring (0–100)
 
-#### HUMAN_SCOPE_CHANGE
-Use when the task set expanded due to new asks, broadened goals, or post-hoc additions.
+Assign each session a severity score to prioritize attention.
 
-#### REPO_FRAGILITY
-Use when hidden coupling, unclear architecture, brittle files, or environmental issues forced extra work.
+Components (sum, clamp 0–100):
+- **Completion failure**: 0–25 (`abandoned = 25`)
+- **Replanning intensity**: 0–15
+- **Scope instability**: 0–15
+- **Rework shape severity**: 0–15
+- **Prompt sufficiency deficit**: 0–10 (`low = 10`)
+- **Root cause impact**: 0–10 (`REPO_FRAGILITY` / `AGENT_ARCHITECTURAL_ERROR` highest)
+- **Hotspot recurrence**: 0–10
 
-#### AGENT_ARCHITECTURAL_ERROR
-Use when the agent chose the wrong approach, wrong files, wrong assumptions, or hallucinated structure.
+Bands:
+- **0–19 Low**
+- **20–39 Moderate**
+- **40–59 Significant**
+- **60–79 High**
+- **80–100 Critical**
 
-#### VERIFICATION_CHURN
-Use when implementation mostly succeeded but tests, validation, QA, or fixes created repeated loops.
+Record:
+- `session_severity_score`
+- `severity_band`
+- `severity_drivers` = top 2–4 contributors
+- `severity_confidence`
 
-#### LEGITIMATE_TASK_COMPLEXITY
-Use when revisions were reasonable given the difficulty and do not strongly indicate avoidable failure.
+Use severity as a prioritization signal, not a verdict. Always explain the drivers.
+Contextualize severity using session intent so research/exploration sessions are not over-penalized.
 
 ---
 
 ## Step 7: Subsystem / File Clustering
 
-Across all conversations, cluster repeated struggle by subsystem, folder, or file mentions.
-
-Examples:
-- `frontend/auth/*`
-- `db.py`
-- `ui.py`
-- `video_pipeline/*`
+Across all conversations, cluster repeated struggle by file, folder, or subsystem.
 
 For each cluster, calculate:
 - number of conversations touching it
 - average revisions
 - completion rate
 - abandonment rate
 - common root causes
+- average severity
 
-Output the top recurring friction zones.
-
-Goal:
-Identify whether struggle is prompt-driven, agent-driven, or concentrated in specific repo areas.
+Goal: identify whether friction is mostly prompt-driven, agent-driven, or concentrated in specific repo areas.
 
 ---
 
-## Step 8: Comparative Cohort Analysis
-
-Compare these cohorts:
+## Step 8: Comparative Cohorts
 
+Compare:
 - first-shot successes vs re-planned sessions
 - completed vs abandoned
 - high prompt sufficiency vs low prompt sufficiency
@@ -296,47 +298,37 @@ For each comparison, identify:
 - which prompt traits correlate with smoother execution
 - which repo traits correlate with repeated struggle
 
-Do not merely restate averages.
-Extract causal-looking patterns cautiously and label them as inference where appropriate.
+Do not just restate averages; extract cautious evidence-backed patterns.
 
 ---
 
 ## Step 9: Non-Obvious Findings
 
 Generate 3–7 findings that are not simple metric restatements.
 
-Good examples:
-- “Most replans happen in sessions with weak file targeting, not weak acceptance criteria.”
-- “Scope growth usually begins after the first successful implementation, suggesting post-success human expansion.”
-- “Auth-related sessions cluster around repo fragility rather than agent hallucination.”
-- “Abandoned work is strongly associated with missing validation criteria.”
-
-Bad examples:
-- “Some sessions had many revisions.”
-- “Some sessions were longer than others.”
-
 Each finding must include:
 - observation
 - why it matters
 - evidence
 - confidence
 
+Examples of strong findings:
+- replans cluster around weak file targeting rather than weak acceptance criteria
+- scope growth often begins after initial success, suggesting post-success human expansion
+- auth-related struggle is driven more by repo fragility than agent hallucination
+
 ---
 
 ## Step 10: Report Generation
 
-Create `session_analysis_report.md` in the current conversation’s brain folder.
-
-Use this structure:
+Create `session_analysis_report.md` with this structure:
 
 # 📊 Session Analysis Report — [Project Name]
 
-**Generated**: [timestamp]
-**Conversations Analyzed**: [N]
+**Generated**: [timestamp]  
+**Conversations Analyzed**: [N]  
 **Date Range**: [earliest] → [latest]
 
----
-
 ## Executive Summary
 
 | Metric | Value | Rating |
@@ -346,171 +338,95 @@ Use this structure:
 | Avg Scope Growth | X% | 🟢/🟡/🔴 |
 | Replan Rate | X% | 🟢/🟡/🔴 |
 | Median Duration | Xm | — |
-| Avg Revision Intensity | X | 🟢/🟡/🔴 |
+| Avg Session Severity | X | 🟢/🟡/🔴 |
+| High-Severity Sessions | X / N | 🟢/🟡/🔴 |
 
-Then include a short narrative summary:
-- what is going well
-- what is breaking down
-- whether the main issue is prompt quality, repo fragility, or workflow discipline
+Thresholds:
+- First-shot: 🟢 >70 / 🟡 40–70 / 🔴 <40
+- Scope growth: 🟢 <15 / 🟡 15–40 / 🔴 >40
+- Replan rate: 🟢 <20 / 🟡 20–50 / 🔴 >50
 
----
+Avg severity guidance:
+- 🟢 <25
+- 🟡 25–50
+- 🔴 >50
+
+Note: avg severity is an aggregate health signal, not the same as per-session severity bands.
+
+Then add a short narrative summary of what is going well, what is breaking down, and whether the main issue is prompt quality, repo fragility, workflow discipline, or validation churn.
 
 ## Root Cause Breakdown
 
 | Root Cause | Count | % | Notes |
 |:---|:---|:---|:---|
-| Spec Ambiguity | X | X% | ... |
-| Human Scope Change | X | X% | ... |
-| Repo Fragility | X | X% | ... |
-| Agent Architectural Error | X | X% | ... |
-| Verification Churn | X | X% | ... |
-| Legitimate Task Complexity | X | X% | ... |
-
----
 
 ## Prompt Sufficiency Analysis
-
 - common traits of high-sufficiency prompts
 - common missing inputs in low-sufficiency prompts
 - which missing prompt ingredients correlate most with replanning or abandonment
 
----
-
 ## Scope Change Analysis
-
 Separate:
 - Human-added scope
 - Necessary discovered scope
 - Agent-introduced scope
 
-Show top offenders in each category.
-
----
-
 ## Rework Shape Analysis
-
-Summarize how sessions tend to fail:
-- early replan then recover
-- progressive scope expansion
-- late verification churn
-- abandonments
-- reopen/reclose cycles
-
----
+Summarize the main failure patterns across sessions.
 
 ## Friction Hotspots
-
-Cluster repeated struggle by subsystem/file/domain.
-Show which areas correlate with:
-- replanning
-- abandonment
-- verification churn
-- agent architectural mistakes
-
----
+Show the files/folders/subsystems most associated with replanning, abandonment, verification churn, and high severity.
 
 ## First-Shot Successes
-
-List the cleanest sessions and extract what made them work:
-- scope boundaries
-- acceptance criteria
-- file targeting
-- validation clarity
-- narrowness of change surface
-
----
+List the cleanest sessions and extract what made them work.
 
 ## Non-Obvious Findings
+List 3–7 evidence-backed findings with confidence.
 
-List 3–7 high-value findings with evidence and confidence.
-
----
+## Severity Triage
+List the highest-severity sessions and say whether the best intervention is:
+- prompt improvement
+- scope discipline
+- targeted skill/workflow
+- repo refactor / architecture cleanup
+- validation/test harness improvement
 
 ## Recommendations
-
-Each recommendation must use this format:
-
-### Recommendation [N]
+For each recommendation, use:
 - **Observed pattern**
 - **Likely cause**
 - **Evidence**
 - **Change to make**
 - **Expected benefit**
 - **Confidence**
 
-Recommendations must be specific, not generic.
-
----
-
 ## Per-Conversation Breakdown
 
-| # | Title | Duration | Scope Δ | Plan Revs | Task Revs | Root Cause | Rework Shape | Complete? |
-|:---|:---|:---|:---|:---|:---|:---|:---|:---|
-
-Add short notes only where meaningful.
+| # | Title | Intent | Duration | Scope Δ | Plan Revs | Task Revs | Root Cause | Rework Shape | Severity | Complete? |
+|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
 
 ---
 
-## Step 11: Auto-Optimize — Improve Future Sessions
+## Step 11: Optional Post-Analysis Improvements
 
-### 11a. Update Project Health State
-# Example path (update to your actual location):
-# `~/.gemini/antigravity/.agent/skills/project-health-state/SKILL.md`
+If appropriate, also:
+- update any local project-health or memory artifact (if present) with recurring failure modes and fragile subsystems
+- generate `prompt_improvement_tips.md` from high-sufficiency / first-shot-success sessions
+- suggest missing skills or workflows when the same subsystem or task sequence repeatedly causes struggle
 
-Update:
-- session analysis metrics
-- recurring fragile files/subsystems
-- recurring failure modes
-- last updated timestamp
-
-### 11b. Generate Prompt Improvement Guidance
-Create `prompt_improvement_tips.md`
-
-Do not give generic advice.
-Instead extract:
-- traits of high-sufficiency prompts
-- examples of effective scope boundaries
-- examples of good acceptance criteria
-- examples of useful file targeting
-- common missing details that led to replans
-
-### 11c. Suggest Missing Skills / Workflows
-If multiple struggle sessions cluster around the same subsystem or repeated sequence, recommend:
-- a targeted skill
-- a repeatable workflow
-- a reusable prompt template
-- a repo note / architecture map
-
-Only recommend workflows when the pattern appears repeatedly.
+Only recommend workflows/skills when the pattern appears repeatedly.
 
 ---
 
 ## Final Output Standard
 
 The workflow must produce:
-1. A metrics summary
-2. A root-cause diagnosis
-3. A subsystem/friction map
-4. A prompt-sufficiency assessment
-5. Evidence-backed recommendations
-6. Non-obvious findings
-
-If evidence is weak, say so.
-Do not overclaim.
-Prefer explicit uncertainty over fake precision.
+1. metrics summary
+2. root-cause diagnosis
+3. prompt-sufficiency assessment
+4. subsystem/friction map
+5. severity triage and prioritization
+6. evidence-backed recommendations
+7. non-obvious findings
 
-
-
-
-
-
-
-
-**How to invoke this skill**  
-Just say any of these in a new conversation:
-- “Run analyze-project on the workspace”
-- “Do a full session analysis report”
-- “Root cause my recent brain/ sessions”
-- “Update project health state”
-
-The agent will automatically discover and use the skill.
+Prefer explicit uncertainty over fake precision.
PATCH

echo "Gold patch applied."
