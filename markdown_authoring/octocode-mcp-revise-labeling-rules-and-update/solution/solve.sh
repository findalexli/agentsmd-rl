#!/usr/bin/env bash
set -euo pipefail

cd /workspace/octocode-mcp

# Idempotency guard
if grep -qF "- **FORBIDDEN:** Using `#1`, `#2`, or any `#<number>` notation to label or refer" "skills/octocode-pull-request-reviewer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/octocode-pull-request-reviewer/SKILL.md b/skills/octocode-pull-request-reviewer/SKILL.md
@@ -30,6 +30,10 @@ Expert code reviewer that performs holistic architectural analysis using Octocod
 - **FORBIDDEN:** Using shell commands (`grep`, `cat`, `find`, `curl`, `gh`) when Octocode MCP tools are available
 - **FORBIDDEN:** Guessing code content without fetching via Octocode MCP
 
+### Finding Numbering (applies to ALL output)
+- **FORBIDDEN:** Using `#1`, `#2`, `#N` or any `#<number>` prefix to label findings or reference them in text. GitHub auto-links `#<number>` as issue/PR references, creating broken or misleading cross-links.
+- Use plain numbering (`1.`, `2.`), lettered labels (`A`, `B`), or descriptive IDs (e.g., `[SEC-1]`, `[BUG-1]`) instead.
+
 ### Precedence Table
 When rules conflict, follow this precedence (highest wins):
 
@@ -310,6 +314,7 @@ GUIDELINES → CONTEXT → USER CHECKPOINT → ANALYSIS → FINALIZE → REPORT
 - **Efficiency**: Batch Octocode MCP queries (1-3 per call). Metadata before content.
 - **Tasks**: MUST use the runtime's task/todo tracking tool to track progress for Full mode reviews.
 - **FORBIDDEN**: Providing timing/duration estimates.
+- **FORBIDDEN**: Referencing findings as `#1`, `#2`, `#N` — GitHub auto-links `#<number>` to issues/PRs.
 </key_principles>
 
 ---
@@ -450,6 +455,11 @@ Base expectation in this SKILL:
 **Template sections**: Executive Summary (goal, risk, recommendation) → Ratings (correctness, security, performance, maintainability) → PR/Changes Health → Guidelines Compliance → Issues (High/Medium/Low with `file:line` + diff fix) → Flow Impact Analysis
 
 **Each finding MUST have**: Location (`file:line`), Confidence (HIGH/MED), Problem description, Code fix (diff format)
+
+### Finding Labels
+- **FORBIDDEN:** Using `#1`, `#2`, or any `#<number>` notation to label or reference findings anywhere in the output. GitHub auto-links `#N` to issues and pull requests, creating broken or misleading cross-links in PR comments.
+- Use plain numbering (`1.`, `2.`), lettered labels (`A`, `B`), or descriptive category IDs (e.g., `[SEC-1]`, `[BUG-1]`, `[ARCH-1]`) instead.
+- This applies to headings, inline references, summary lists, and any other mention of finding identifiers.
 </output_structure>
 
 ---
@@ -476,4 +486,5 @@ Use the full checklist from:
 - [ ] Target/mode resolved (including file-scoped local checks when requested)
 - [ ] Phase 4 analysis complete with evidence and confidence labels
 - [ ] Findings are actionable, deduplicated, and scoped correctly
+- [ ] No `#<number>` notation used in any finding label or reference
 </verification_base>
PATCH

echo "Gold patch applied."
