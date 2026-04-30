#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prd-taskmaster

# Idempotency guard
if grep -qF "**IMPORTANT**: Generate a TDD workflow guide for the project using the template," "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -36,18 +36,19 @@ Do NOT activate for:
 
 **Complete Automation**: Provides 4 autonomous execution modes with git policies, progress logging, and datetime tracking.
 
-## Workflow Overview (12 Steps)
+## Workflow Overview (13 Steps)
 
 1. **Enable Plan Mode & Check State** - Resume detection + interactive prompts
 2. **Detect Existing PRD** - Smart detection with execute/update/replace options
 3. **Detect Taskmaster** - MCP > CLI > Block if missing
 4. **Discovery Questions** - 12+ detailed questions (if generating new PRD)
 5. **Initialize Taskmaster** - Via MCP/CLI (if not already initialized)
-6. **Generate PRD** - Comprehensive 11-section document (if creating new)
+6. **Generate PRD** - Load template and fill with discovery answers
 7. **Validate Quality** - 13 automated checks
 8. **Parse & Expand** - Combined operation with research
 9. **Insert User Tests** - Checkpoint every 5 tasks
 10. **Setup Tracking** - DateTime, rollback, accuracy scripts
+10.5. **Generate CLAUDE.md** - TDD workflow guide from template
 11. **Choose Next Action** - Handoff to TaskMaster OR autonomous execution
 12. **Summary & Start** - Present overview and begin work
 
@@ -344,69 +345,57 @@ taskmaster init --yes --store-tasks-in-git --rules=claude
 
 ### Step 6: Generate Comprehensive PRD
 
-Write PRD to `.taskmaster/docs/prd.md`
-
-**11 Essential Sections:**
-
-1. **Executive Summary** (2-3 sentences: problem + solution + impact)
-
-2. **Problem Statement**
-   - Current situation and pain points
-   - User impact (who's affected, how)
-   - Business impact (cost, opportunity)
-   - Why solve this now
-
-3. **Goals & Success Metrics** (SMART format)
-   - 3-5 specific goals
-   - Each with: metric, baseline, target, timeframe
-   - Example: "Increase user activation from 45% to 65% within 3 months"
-
-4. **User Stories** (Agile format with taskmaster focus)
-   - As a [user], I want to [action] so that I can [benefit]
-   - Detailed acceptance criteria (becomes task completion criteria)
-   - Each story suggests 1-3 implementation tasks
-
-5. **Functional Requirements**
-   - Numbered (REQ-001, REQ-002, etc.)
-   - Prioritized (Must/Should/Could have)
-   - Each requirement is atomic and testable
-   - Includes implementation hints for task breakdown
-
-6. **Non-Functional Requirements**
-   - Performance (with specific targets: "< 200ms p95")
-   - Security (authentication, encryption, compliance)
-   - Scalability (user load, data volume)
-   - Reliability (uptime, error rates)
-   - Accessibility (WCAG standards)
-   - Compatibility (browsers, devices, OS)
-
-7. **Technical Considerations**
-   - Architecture implications
-   - API specifications (with request/response examples)
-   - Database schema changes (with SQL/schema examples)
-   - Dependencies (internal and external)
-   - Migration strategy (for existing systems)
-   - Testing strategy (unit, integration, e2e)
-
-8. **Implementation Roadmap** (Taskmaster Optimization)
-   - Phase breakdown (Phase 1, 2, 3...)
-   - Task sequencing (what depends on what)
-   - Complexity estimates (for taskmaster scheduling)
-   - Suggested task breakdown per requirement
-
-9. **Out of Scope**
-   - Explicitly list what will NOT be included
-   - Prevents scope creep
-   - Note future considerations
-
-10. **Open Questions & Risks**
-    - Unresolved decisions with owners
-    - Known risks with mitigation strategies
-    - Areas needing further research
-
-11. **Validation Checkpoints**
-    - Milestones where we verify progress
-    - Quality gates for task completion
+**IMPORTANT**: Use the PRD template from `templates/` directory as the base structure.
+
+**Template Selection:**
+```
+1. Read PRD template based on project complexity:
+   - Complex/Standard projects: Use Read tool to load templates/taskmaster-prd-comprehensive.md
+   - Simple features: Use Read tool to load templates/taskmaster-prd-minimal.md
+
+2. Template provides:
+   - Complete section structure with placeholders
+   - Examples for each section
+   - Taskmaster-specific hints and formatting
+```
+
+**Generation Process:**
+```
+1. Load template:
+   - Use Read tool: templates/taskmaster-prd-comprehensive.md (default)
+   - Or: templates/taskmaster-prd-minimal.md (if user requested minimal)
+
+2. Fill template with user's answers from Step 4:
+   - Replace [placeholders] with actual content
+   - Expand examples with project-specific details
+   - Add technical depth based on discovery answers
+
+3. Write completed PRD:
+   - Output to: .taskmaster/docs/prd.md
+   - Preserve template structure and formatting
+```
+
+**Template contains 12 sections:**
+1. Executive Summary
+2. Problem Statement
+3. Goals & Success Metrics
+4. User Stories
+5. Functional Requirements
+6. Non-Functional Requirements
+7. Technical Considerations
+8. Implementation Roadmap
+9. Out of Scope
+10. Open Questions & Risks
+11. Validation Checkpoints
+12. Appendix: Task Breakdown Hints
+
+**Output:**
+```
+✅ PRD Generated from template
+   Template: taskmaster-prd-comprehensive.md
+   Output: .taskmaster/docs/prd.md
+   Sections: 12 (all populated)
+```
 
 ---
 
@@ -623,6 +612,89 @@ See sections below for complete script implementations.
 
 ---
 
+### Step 10.5: Generate CLAUDE.md (TDD Workflow Guide)
+
+**IMPORTANT**: Generate a TDD workflow guide for the project using the template, but only if one doesn't already exist.
+
+**Pre-Check (REQUIRED):**
+```
+1. Check if CLAUDE.md already exists:
+   - Use Glob tool: ./CLAUDE.md
+   - If EXISTS → Skip generation, show message:
+     "ℹ️ CLAUDE.md already exists. Skipping generation to preserve your configuration."
+   - If NOT EXISTS → Proceed with generation
+
+2. Check if codex.md already exists (for later):
+   - Use Glob tool: ./codex.md
+   - Store result for Step 4 below
+```
+
+**Template Loading (only if CLAUDE.md doesn't exist):**
+```
+1. Read the CLAUDE.md template:
+   - Use Read tool: templates/CLAUDE.md.template
+
+2. Template contains:
+   - TDD workflow instructions (RED → GREEN → REFACTOR)
+   - Taskmaster integration commands
+   - Agent usage guidelines
+   - Validation & quality gates
+   - Project-specific placeholders
+```
+
+**Placeholder Replacement:**
+```
+Replace these placeholders with project-specific values from Step 4 discovery:
+
+{{PROJECT_NAME}}        → User's project/feature name
+{{TECH_STACK}}          → Tech stack from discovery (e.g., "React, Node.js, PostgreSQL")
+{{ARCHITECTURE_OVERVIEW}} → Brief architecture description
+{{KEY_DEPENDENCIES}}    → Main dependencies identified
+{{TESTING_FRAMEWORK}}   → Testing framework (e.g., "Jest", "Vitest", "pytest")
+{{DEV_ENVIRONMENT}}     → Development environment setup
+{{TEST_COMMAND}}        → Test command (e.g., "npm test", "pytest")
+```
+
+**Generation Process:**
+```
+1. Pre-check: Skip if CLAUDE.md exists (see Pre-Check above)
+
+2. Load template:
+   - Use Read tool: templates/CLAUDE.md.template
+
+3. Fill placeholders with discovery answers:
+   - If value unknown, use sensible default or "[To be configured]"
+
+4. Write to project root:
+   - Output to: ./CLAUDE.md (project root)
+
+5. Ask about Codex (only if codex.md doesn't exist):
+   - Use AskUserQuestion: "Are you using Codex in addition to Claude Code?"
+   - If yes AND codex.md doesn't exist: Also write to ./codex.md (identical content)
+   - If codex.md exists: Skip, show "ℹ️ codex.md already exists."
+```
+
+**Output:**
+```
+[If CLAUDE.md doesn't exist]
+✅ CLAUDE.md Generated
+   Template: templates/CLAUDE.md.template
+   Output: ./CLAUDE.md
+   Contains: TDD workflow, taskmaster integration, quality gates
+
+[If CLAUDE.md exists]
+ℹ️ CLAUDE.md already exists - skipped generation
+
+[If Codex selected AND codex.md doesn't exist]
+✅ codex.md Generated (identical to CLAUDE.md)
+   Output: ./codex.md
+
+[If codex.md exists]
+ℹ️ codex.md already exists - skipped generation
+```
+
+---
+
 ---
 
 ### Step 11: Choose Next Action (Handoff vs Autonomous Execution)
PATCH

echo "Gold patch applied."
