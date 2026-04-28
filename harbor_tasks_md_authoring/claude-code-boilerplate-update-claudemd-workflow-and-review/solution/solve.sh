#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-boilerplate

# Idempotency guard
if grep -qF "**CRITICAL:** Steps 3-4 (TDD), Steps 7-9 (Impact Verification), and Steps 11-15 " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -47,9 +47,10 @@
 12. [Documentation Standards](#12-documentation-standards)
 13. [Git Workflow](#13-git-workflow)
 14. [Issue Hierarchy](#14-issue-hierarchy)
-15. [AI Agent Workflow](#15-ai-agent-workflow)
+15. [AI Agent Workflow](#15-ai-agent-workflow) - *"No Code, No Problem"*
     - [15.0 TDD-First Principle (ABSOLUTE REQUIREMENT)](#150-tdd-first-principle-absolute-requirement)
     - [15.0.1 Zero-Impact Implementation (ABSOLUTE REQUIREMENT)](#1501-zero-impact-implementation-absolute-requirement)
+    - [15.4 Review Requirements (Score ≥ 9.5 to Merge)](#154-review-requirements-score-based-approval)
 16. [Claude Code Configuration](#16-claude-code-configuration)
 
 ---
@@ -885,6 +886,18 @@ Task details.
 
 ## 15. AI Agent Workflow
 
+```
+┌─────────────────────────────────────────────────────────────┐
+│                                                             │
+│              "NO CODE, NO PROBLEM"                          │
+│                                                             │
+│   The best code is no code. The best fix is prevention.     │
+│   Write only what's necessary. Delete what's not.           │
+│   Simplicity is the ultimate sophistication.                │
+│                                                             │
+└─────────────────────────────────────────────────────────────┘
+```
+
 ### 15.0 TDD-First Principle (ABSOLUTE REQUIREMENT)
 
 **TEST-DRIVEN DEVELOPMENT IS NON-NEGOTIABLE. NO EXCEPTIONS. EVER.**
@@ -1303,23 +1316,85 @@ If a breaking change is ABSOLUTELY necessary:
 | 8 | - | Run quality gates (typecheck, lint, test, build) |
 | 9 | - | **Verify no impact** to existing functionality |
 | 10 | - | Commit and create PR |
-| 11 | Principal Agent | Review #1: Initial review |
-| 12 | Fullstack Agent | Address feedback (following TDD for any changes) |
-| 13 | Principal Agent | Review #2: Verification |
-| 14 | Fullstack Agent | Address feedback (following TDD for any changes) |
-| 15 | Principal Agent | Review #3: Final approval |
+| 11 | All Review Agents | **Team Review** - Each agent scores (1-10) + provides feedback |
+| 12 | - | **Calculate average score** across all reviewers |
+| 13 | Fullstack Agent | If avg < 9.5: **Fix ALL issues** from ALL reviewers |
+| 14 | - | **Repeat steps 11-13** until average score ≥ 9.5 |
+| 15 | - | **APPROVED** - Ready to merge when score ≥ 9.5 |
 
-**CRITICAL:** Steps 3-4 (TDD) and Steps 7-9 (Impact Verification) are NON-NEGOTIABLE.
+**CRITICAL:** Steps 3-4 (TDD), Steps 7-9 (Impact Verification), and Steps 11-15 (Score ≥ 9.5) are NON-NEGOTIABLE.
 
-### 15.4 Minimum Review Requirements
+### 15.4 Review Requirements (Score-Based Approval)
 
-**Each PR MUST receive at least 3 reviews before merge:**
+**PRs are approved when average team review score reaches 9.5+/10.**
 
-| Review | Focus |
-|--------|-------|
-| Review #1 | Critical issues, architecture, security |
-| Review #2 | Verify fixes, deeper analysis, edge cases |
-| Review #3 | Final verification, merge decision |
+```
+┌─────────────────────────────────────────────────────────────┐
+│  REVIEW CYCLE - ITERATE UNTIL SCORE 9.5+                    │
+│                                                             │
+│  ┌─────────────────┐                                        │
+│  │  TEAM REVIEW    │  All agents review the PR              │
+│  │  (Score 1-10)   │  Each provides score + feedback        │
+│  └────────┬────────┘                                        │
+│           │                                                 │
+│           ▼                                                 │
+│  ┌─────────────────┐                                        │
+│  │ CALCULATE AVG   │  Average all agent scores              │
+│  │    SCORE        │                                        │
+│  └────────┬────────┘                                        │
+│           │                                                 │
+│           ▼                                                 │
+│  ┌─────────────────┐      NO     ┌─────────────────┐        │
+│  │  Score ≥ 9.5?   │────────────►│  FIX ALL ISSUES │        │
+│  └────────┬────────┘             │  from feedback  │        │
+│           │ YES                  └────────┬────────┘        │
+│           │                               │                 │
+│           ▼                               │                 │
+│  ┌─────────────────┐                      │                 │
+│  │    APPROVED     │◄─────────────────────┘                 │
+│  │  Ready to merge │      (repeat review cycle)             │
+│  └─────────────────┘                                        │
+└─────────────────────────────────────────────────────────────┘
+```
+
+#### Review Scoring Criteria
+
+| Score | Meaning | Action Required |
+|-------|---------|-----------------|
+| 10 | Perfect - No issues | Ready to merge |
+| 9 | Excellent - Minor suggestions only | Optional improvements |
+| 8 | Good - Small issues exist | Must fix before merge |
+| 7 | Acceptable - Notable issues | Fix required |
+| 6 | Below Standard - Multiple issues | Significant rework needed |
+| ≤5 | Unacceptable - Major problems | Complete revision required |
+
+#### Review Process
+
+| Step | Action | Outcome |
+|------|--------|---------|
+| 1 | Submit PR | Team review begins |
+| 2 | Each agent reviews | Provides score (1-10) + detailed feedback |
+| 3 | Calculate average | Sum of scores / number of reviewers |
+| 4 | If avg < 9.5 | Fix ALL issues identified by ALL reviewers |
+| 5 | Re-submit for review | Repeat steps 2-4 |
+| 6 | If avg ≥ 9.5 | **APPROVED** - Ready to merge |
+
+#### Review Focus by Agent
+
+| Agent | Review Focus | Scoring Weight |
+|-------|--------------|----------------|
+| Principal Agent | Code quality, architecture, security, best practices | Equal |
+| QA Agent | Test coverage, test quality, edge cases, regression | Equal |
+| UI/UX Agent | User experience, accessibility, design consistency | Equal |
+| Solution Architect | Scalability, system design, integration patterns | Equal |
+
+#### Important Rules
+
+- **ALL issues must be fixed** - No "will fix later" or "minor, can skip"
+- **ALL reviewers must re-review** after fixes
+- **Score MUST reach 9.5+** - No exceptions, no shortcuts
+- **Each cycle is fresh** - Previous scores don't carry over
+- **Detailed feedback required** - Scores without justification are invalid
 
 ### 15.5 Team Agent Roles
 
@@ -1397,11 +1472,31 @@ If a breaking change is ABSOLUTELY necessary:
                     │
                     ▼
 ┌─────────────────────────────────────────────┐
-│  8-12. REVIEW CYCLES (3 minimum)            │
-│     - Any changes follow TDD cycle          │
-│     - Re-verify zero impact after changes   │
+│  8. TEAM REVIEW (All Agents)                │
+│     - Each agent scores 1-10                │
+│     - Each provides detailed feedback       │
+│     - Calculate average score               │
 └─────────────────────────────────────────────┘
-```
+                    │
+                    ▼
+           ┌───────────────┐
+           │ Avg Score     │
+           │   ≥ 9.5?      │
+           └───────┬───────┘
+                   │
+         NO ◄──────┴──────► YES
+          │                  │
+          ▼                  ▼
+┌─────────────────────┐  ┌─────────────────────┐
+│  FIX ALL ISSUES     │  │     APPROVED        │
+│  from ALL reviewers │  │  Ready to merge     │
+│  (follow TDD cycle) │  │                     │
+└──────────┬──────────┘  └─────────────────────┘
+           │
+           └──────► REPEAT (back to step 8)
+```
+
+**"NO CODE, NO PROBLEM"** - Iterate until excellence. No shortcuts.
 
 ### 15.7 Epic Branch Strategy
 
PATCH

echo "Gold patch applied."
