#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-toolkit

# Idempotency guard
if grep -qF "Read `references/phase-2-dispatch-agents.md` for the full dispatch prompt (11 re" "skills/sapcc-audit/SKILL.md" && grep -qF "Some findings may overlap (e.g., dead-code agent and architecture agent flag the" "skills/sapcc-audit/references/output-templates.md" && grep -qF "If neither command surfaces an sapcc module path or sapcc imports, stop immediat" "skills/sapcc-audit/references/phase-1-discover-commands.md" && grep -qF "- **Use gopls MCP tools when available**: `go_workspace` to detect workspace str" "skills/sapcc-audit/references/phase-2-dispatch-agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/sapcc-audit/SKILL.md b/skills/sapcc-audit/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: sapcc-audit
 description: "Full-repo SAP CC Go compliance audit against review standards."
-version: 2.0.0
+version: 2.1.0
 user-invocable: false
 command: /sapcc-audit
 agent: golang-general-engineer
@@ -37,263 +37,78 @@ Review every package against established review standards. Not checklist complia
 
 ---
 
-## Instructions
-
-### Phase 1: DISCOVER
-
-**Goal**: Map the repository and plan the package segmentation.
-
-**Step 1: Verify this is an sapcc project**
+## Reference Loading Table
 
-```bash
-head -5 go.mod  # Check module path
-grep "sapcc" go.mod  # Check for sapcc imports
-```
+| Signal | Load This File | When |
+|--------|---------------|------|
+| Phase 1 begins | `references/phase-1-discover-commands.md` | Detection commands, package mapping, segmentation table |
+| Phase 2 begins | `references/phase-2-dispatch-agents.md` | Full dispatch prompt and per-domain review checklist (11 areas) |
+| Phase 3 begins | `references/output-templates.md` | Report scaffold, per-finding format, severity guide |
 
-If not an sapcc project, stop immediately.
+Load each reference file at the start of its phase. Do not load all three upfront.
 
-**Step 2: Map all packages**
-
-```bash
-find . -name "*.go" -not -path "./vendor/*" | sed 's|/[^/]*$||' | sort -u
-```
+---
 
-Count files per package. This determines how to segment for parallel agents.
+## Instructions
 
-**Step 3: Plan agent segmentation**
+### Phase 1: DISCOVER
 
-Group packages so each agent gets 5-15 files (sweet spot for thorough review).
+**Goal**: Map the repository and plan the package segmentation.
 
-Example for a repo with `cmd/`, `internal/api/`, `internal/config/`, `internal/storage/`, `internal/router/`, etc.:
+Read `references/phase-1-discover-commands.md` for the exact detection commands, segmentation table, and file-count queries.
 
-| Agent | Packages | Focus |
-|-------|----------|-------|
-| 1 | `cmd/` + `main.go` files | Startup patterns, CLI structure |
-| 2 | `internal/api/` | HTTP handlers, error responses, routing |
-| 3 | `internal/config/` + `internal/auth/` | Configuration, auth patterns |
-| 4 | `internal/storage/` + `internal/wal/` | Storage, persistence, error handling |
-| 5 | `internal/router/` + `internal/source/` | Core logic, concurrency |
-| 6 | `internal/integrity/` + `internal/limiter/` + remaining | Crypto, rate limiting |
-| 7 | All `*_test.go` files | Testing patterns, assertions |
+Verify this is an sapcc project (sapcc imports in go.mod). If not, stop immediately.
 
-Adjust based on actual package sizes. Aim for 5-8 agents.
+Map all packages, count files per package, and produce a segmentation table (5–8 agents, 5–15 files each).
 
 **Gate**: Packages mapped, agents planned. Proceed to Phase 2.
 
+---
+
 ### Phase 2: DISPATCH
 
 **Goal**: Launch parallel agents that review packages against project standards.
 
-**Principle: Read the actual code.** Agents MUST use the Read tool to read every .go file in their assigned packages. Read every file directly rather than guessing from names or grep output. Use gopls MCP tools when available: `go_workspace` to detect workspace structure, `go_file_context` after reading each .go file for intra-package dependency understanding, `go_symbol_references` to verify type usage across packages (critical for export decisions), `go_package_api` to inspect package APIs, `go_diagnostics` to verify any fixes.
-
-**Principle: Real review, not checklists.** The primary question for every function is: "Would this pass review?" not "does it follow a checklist." A real reviewer reads code holistically and reacts to architectural issues, not just mechanical patterns.
-
-**Principle: Segment by package, not by concern.** Dispatch agents by package groups, NOT by concern area. Each agent reviews its packages holistically (errors + architecture + patterns + tests together), exactly like a real PR review. Real code review reads a file holistically — an error handling issue might actually be an architecture issue. Segmenting by concern produces shallow findings.
-
-**Code-level findings only.** Every finding MUST include the actual code snippet and a concrete fix showing what it should become. Every finding must include a concrete code-level fix. Show current code and what it should become.
-
-**Each agent gets this dispatch prompt:**
-
-```
-You are reviewing code in an SAP Converged Cloud Go project against established
-review standards. Your job is to find things that would actually be commented on
-or rejected in a PR.
-
-PACKAGES TO REVIEW: [list of packages with full paths]
-
-Read EVERY .go file in these packages using the Read tool. For each file:
-
-1. **Over-engineering** (Lead Reviewer's #1 Concern)
-   - Interfaces with only one implementation? → "Just use the concrete type." Project convention: only create interfaces when there are 2+ real implementations.
-   - Wrapper function that adds nothing? → "Delete this, call the real function"
-   - Struct for one-time JSON? → "Use fmt.Sprintf + json.Marshal" (per project convention)
-   - Option struct for constructor? → "Just use positional params." Project convention uses 7-8 positional params, always positional params.
-   - Config file/viper? → "Use osext.MustGetenv." Project convention uses environment variables exclusively. Pure env vars only.
-
-2. **Dead code**
-   - Exported functions with no callers outside the package? Use Grep to check: `grep -r "FunctionName" --include="*.go"`. If no callers exist, flag it.
-   - Interface methods unused
-   - Fields set but unread
-   - Entire packages imported but barely used
-   - "TODO: remove" comments on code that should already be gone
-
-3. **Error messages** (Secondary Reviewer's #1 Concern)
-   - `http.Error(w, "internal error", 500)` — useless to the caller
-   - Error wrapping: uses %w when caller needs errors.Is/As, %s with .Error() to intentionally break chain
-   - Message format: "cannot <operation>: %w" or "while <operation>: %w" with relevant identifiers
-   - Would a user/operator reading this know what to do?
-   - "internal error" with no context = CRITICAL
-   - Return the primary error; log secondary/cleanup errors. Primary error returned, secondary/cleanup errors logged.
-
-4. **Constructor patterns**
-   - Constructor should be `NewX(deps...) *X` — returns infallibly (no error) (construction is infallible)
-   - Uses positional struct literal init: `&API{cfg, ad, fd, sd, ...}` (no field names)
-   - Injects default functions for test doubles: `time.Now`, etc.
-   - Override pattern for test doubles: fluent `OverrideTimeNow(fn) *T` methods
-
-5. **Interface contracts**
-   - If the package implements an interface from another package: Read the interface definition
-   - Check if the implementation actually satisfies the contract
-   - Does it return correct error types? Default values where errors are expected?
-   - Interfaces should be defined in the consumer package, not the implementation package
-
-6. **Copy-paste structs**
-   - Two structs with the same fields (one for internal, one for API response)?
-   - Handler functions that are 90% identical (extract the common pattern)
-   - Duplicated validation logic
-
-7. **HTTP handler patterns** (Must match keppel patterns)
-   - Handlers: methods on *API with `handleVerbResource(w, r)` signature
-   - Auth: called inline at top of handler, NOT middleware
-   - JSON decode: `json.NewDecoder` + `DisallowUnknownFields()`
-   - Responses: `respondwith.JSON(w, status, map[string]any{"key": val})`
-   - Internal errors: `respondwith.ObfuscatedErrorText(w, err)` — hides 500s from clients
-   - Route registration: one `AddTo(*mux.Router)` per API domain, composed via `httpapi.Compose`
-
-8. **Database patterns**
-   - SQL queries as package-level `var` with `sqlext.SimplifyWhitespace()`
-   - PostgreSQL `$1, $2` params (always `$1, $2` (PostgreSQL syntax))
-   - gorp for simple CRUD, raw SQL for complex queries
-   - Transactions: `db.Begin()` + `defer sqlext.RollbackUnlessCommitted(tx)`
-   - NULL: `Option[T]` (from majewsky/gg/option), not `*T` pointers
-
-9. **Type patterns**
-   - Named string types for domain concepts: `type AccountName string`
-   - String enums with typed constants (NOT iota): `const CleanSeverity VulnerabilityStatus = "Clean"`
-   - Model types use `db:"column"` tags; API types use `json:"field"` tags — separate types
-   - Pointer receivers for all struct methods (value receivers only for tiny data-only types)
-
-10. **Logging patterns**
-    - `logg.Fatal` ONLY in cmd/ packages for startup failures
-    - `logg.Error` for secondary/cleanup errors (only for secondary/cleanup errors)
-    - `logg.Info` for operational events
-    - Use logg package for all logging
-    - Panics only for impossible states, annotated with "why was this not caught by Validate!?"
-
-11. **Mixed approaches** (Pattern consistency)
-    - Some handlers return JSON errors, others return text/plain
-    - Some constructors panic on nil args, others return errors
-    - Some packages use logg, others use log
-
-For EACH finding, output:
-
-### [MUST-FIX / SHOULD-FIX / NIT]: [One-line summary]
-**File**: `path/to/file.go:LINE`
-**Convention**: "[What a lead reviewer would actually write in a PR comment]"
-
-**Current code**:
-\`\`\`go
-[actual code from the file, 3-10 lines]
-\`\`\`
-
-**Should be**:
-\`\`\`go
-[what the code should look like after fixing]
-\`\`\`
-
-**Why**: [One sentence explaining the principle]
-
----
-
-SEVERITY GUIDE:
-- MUST-FIX: Would block the PR (data loss, interface violation, wrong behavior)
-- SHOULD-FIX: Would get a strong review comment (dead code, copy-paste, bad errors)
-- NIT: Would get a comment but not block (style, naming, minor simplification)
-
-Skip:
-- Generic Go best practices (t.Parallel, DisallowUnknownFields, context.Context first)
-- Things that are actually fine but could theoretically be "better"
-- Suggestions that add complexity without clear benefit
+Read `references/phase-2-dispatch-agents.md` for the full dispatch prompt (11 review areas: over-engineering, dead code, error messages, constructors, interface contracts, copy-paste, HTTP handlers, database patterns, type patterns, logging, mixed approaches).
 
-Focus on:
-- Real over-engineering (lead reviewer's #1 concern)
-- Actually useless error messages (secondary reviewer's #1 concern)
-- Dead code that should be deleted
-- Interface contract bugs
-- Constructor/config patterns that diverge from keppel patterns
-- Inconsistent patterns within the same repo
-```
+Use the standard dispatch prompt verbatim, substituting the assigned package list.
 
-**Dispatch all agents in a single message using the Task tool with subagent_type=golang-general-engineer.**
+**Dispatch all agents in a single message using the Task tool with `subagent_type=golang-general-engineer`.**
 
 **Gate**: All agents dispatched. Proceed to Phase 3.
 
+---
+
 ### Phase 3: COMPILE REPORT
 
 **Goal**: Aggregate findings into a code-level compliance report.
 
-**Step 1: Collect and deduplicate**
-
-Some findings may overlap (e.g., dead code agent and architecture agent flag the same unused function). Deduplicate by file:line.
-
-**Step 2: Write the report**
-
-Create `sapcc-audit-report.md`:
-
-```markdown
-# SAPCC Code Review: [repo name]
-
-**Reviewed by**: Lead & secondary reviewer standards (simulated)
-**Date**: [date]
-**Packages**: [N] packages, [M] Go files
+Read `references/output-templates.md` for the report scaffold, per-finding format, and deduplication rules.
 
-## Verdict
-
-[One paragraph: Would this pass review? What's the overall impression?]
-
-## Must-Fix (Would Block PR)
-
-[Each finding with current/should-be code]
-
-## Should-Fix (Strong Review Comments)
-
-[Each finding with current/should-be code]
-
-## Nits
-
-[Each finding, brief]
-
-## What's Done Well
-
-[Genuine positives — things a reviewer would note approvingly]
-
-## Package-by-Package Summary
-
-| Package | Files | Must-Fix | Should-Fix | Nit | Verdict |
-|---------|-------|----------|-----------|-----|---------|
-| internal/api | N | X | Y | Z | [emoji] |
-| ... | | | | | |
-```
-
-**Step 3: Display summary**
-
-Show the verdict, must-fix count, and top 5 findings inline. Point to the full report file.
+Deduplicate by `file:line`. Write `sapcc-audit-report.md`. Display verdict, must-fix count, and top 5 findings inline.
 
 **Gate**: Report complete.
 
 ---
 
 ## Error Handling
 
-### Failure modes and recovery
-
 | Scenario | Response |
 |----------|----------|
-| Not an sapcc project | Stop immediately. Print message: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)." |
-| Agents cannot read a file | Log and continue. File may be binary or inaccessible. Flag in the report under "Warnings." |
-| gopls MCP tools unavailable | Fall back to manual grep-based analysis. Note in the report that type-aware analysis was unavailable. |
-| Too many packages (>30) | Split into >8 agents. Ensure each still gets 5-15 files for depth. |
-| Agent finds no violations | Report is valid. Not every package has violations. Output empty sections for unused severity levels. |
-
-### Principles
+| Not an sapcc project | Stop immediately. Print: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)." |
+| Agents cannot read a file | Log and continue. Flag in the report under "Warnings." |
+| gopls MCP tools unavailable | Fall back to manual grep-based analysis. Note in the report. |
+| Too many packages (>30) | Split into >8 agents. Ensure each still gets 5-15 files. |
+| Agent finds no violations | Report is valid. Output empty sections for unused severity levels. |
 
-- **Audit only**: READS and REPORTS. Does NOT modify code unless explicitly asked with `--fix`.
-- **Skip generic findings**: Skip reporting `DisallowUnknownFields`, `t.Parallel()`, or other generic Go best practices unless they are genuinely wrong in context. Focus on sapcc-specific patterns.
-- **Rationalization guard**: Focus on findings that would actually be commented on in a real PR review. Focus on things that would actually be commented on in a real PR review.
+**Audit only**: READS and REPORTS. Does NOT modify code unless explicitly asked with `--fix`.
 
 ---
 
-## References
+## Integration
+
+- **Router**: `/do` routes via "sapcc audit", "sapcc compliance", "sapcc lead review"
+- **Pairs with**: `go-patterns` (the rules), `golang-general-engineer` (the executor)
 
 ### Per-agent reference loading (included in each agent's dispatch prompt based on assigned packages)
 
@@ -306,15 +121,4 @@ Show the verdict, must-fix count, and top 5 findings inline. Point to the full r
 | Build/CI config | `build-ci-detailed.md` |
 | Import-heavy files | `library-reference.md` |
 
-### Always available for calibration (load only when needed)
-
-- `quality-issues.md` — Quick-check findings against known anti-patterns
-- `review-standards-lead.md` — Calibrate review tone and severity
-
-**Note**: Load reference files only for domain-specific depth, rather than giving every agent to read the full sapcc-code-patterns.md. The rules are already inline in the dispatch prompt. Load reference files only for domain-specific depth.
-
-### Integration
-
-- **Router**: `/do` routes via "sapcc audit", "sapcc compliance", "sapcc lead review"
-- **Pairs with**: `go-patterns` (the rules), `golang-general-engineer` (the executor)
-- **Prerequisite**: `go-patterns` must be loaded so agents have the rules
+Always available for calibration (load only when needed): `quality-issues.md`, `review-standards-lead.md`.
diff --git a/skills/sapcc-audit/references/output-templates.md b/skills/sapcc-audit/references/output-templates.md
@@ -0,0 +1,107 @@
+# Output Templates
+
+> **Load when**: Phase 3 (COMPILE REPORT) begins.
+> **Purpose**: Report scaffold, per-agent finding format, and severity guide for the final audit output.
+
+---
+
+## Report File Template
+
+Create `sapcc-audit-report.md` with this structure:
+
+```markdown
+# SAPCC Code Review: [repo name]
+
+**Reviewed by**: Lead & secondary reviewer standards (simulated)
+**Date**: [date]
+**Packages**: [N] packages, [M] Go files
+
+## Verdict
+
+[One paragraph: Would this pass review? What's the overall impression?]
+
+## Must-Fix (Would Block PR)
+
+[Each finding with current/should-be code]
+
+## Should-Fix (Strong Review Comments)
+
+[Each finding with current/should-be code]
+
+## Nits
+
+[Each finding, brief]
+
+## What's Done Well
+
+[Genuine positives — things a reviewer would note approvingly]
+
+## Package-by-Package Summary
+
+| Package | Files | Must-Fix | Should-Fix | Nit | Verdict |
+|---------|-------|----------|-----------|-----|---------|
+| internal/api | N | X | Y | Z | [emoji] |
+| ... | | | | | |
+```
+
+---
+
+## Per-Finding Format
+
+Each finding from dispatched agents uses this format:
+
+```
+### [MUST-FIX / SHOULD-FIX / NIT]: [One-line summary]
+**File**: `path/to/file.go:LINE`
+**Convention**: "[What a lead reviewer would actually write in a PR comment]"
+
+**Current code**:
+[actual code from the file, 3-10 lines]
+
+**Should be**:
+[what the code should look like after fixing]
+
+**Why**: [One sentence explaining the principle]
+```
+
+---
+
+## Severity Guide
+
+| Level | Meaning | Action |
+|-------|---------|--------|
+| MUST-FIX | Would block the PR: data loss, interface violation, wrong behavior | Always include; leads the report |
+| SHOULD-FIX | Strong review comment: dead code, copy-paste, bad errors | Include with full before/after |
+| NIT | Comment but not blocking: style, naming, minor simplification | Brief — no full code blocks needed |
+
+---
+
+## Deduplication Rule
+
+Some findings may overlap (e.g., dead-code agent and architecture agent flag the same unused function). Deduplicate by `file:line`. When two agents flag the same location, keep the finding with the higher severity.
+
+---
+
+## Summary Display (Inline)
+
+After writing the report file, display to the user:
+1. Overall verdict (one sentence)
+2. Must-fix count
+3. Top 5 findings (file + one-line summary only)
+4. Path to full report
+
+Example:
+
+```
+Verdict: Needs work before review — 3 must-fix issues found.
+Must-Fix: 3 | Should-Fix: 11 | Nits: 7
+
+Top findings:
+1. [MUST-FIX] internal/api/handler.go:42 — interface with single implementation
+2. [MUST-FIX] internal/storage/db.go:87 — "internal error" with no context
+3. [MUST-FIX] internal/auth/auth.go:15 — constructor returns error (infallibility violation)
+4. [SHOULD-FIX] internal/config/config.go:33 — viper config file instead of osext.MustGetenv
+5. [SHOULD-FIX] internal/api/routes.go:61 — duplicate handler (90% identical to routes.go:89)
+
+Full report: sapcc-audit-report.md
+```
diff --git a/skills/sapcc-audit/references/phase-1-discover-commands.md b/skills/sapcc-audit/references/phase-1-discover-commands.md
@@ -0,0 +1,68 @@
+# Phase 1: DISCOVER — Detection Commands
+
+> **Load when**: Phase 1 (DISCOVER) begins.
+> **Purpose**: Go grep/vet detection commands for mapping the repository and validating it is an sapcc project.
+
+---
+
+## Step 1: Verify sapcc Project
+
+```bash
+head -5 go.mod  # Check module path
+grep "sapcc" go.mod  # Check for sapcc imports
+```
+
+If neither command surfaces an sapcc module path or sapcc imports, stop immediately and report: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)."
+
+---
+
+## Step 2: Map All Packages
+
+```bash
+find . -name "*.go" -not -path "./vendor/*" | sed 's|/[^/]*$||' | sort -u
+```
+
+Count files per package. This determines how to segment for parallel agents.
+
+---
+
+## Step 3: Plan Agent Segmentation
+
+Group packages so each agent gets 5–15 files (sweet spot for thorough review). Target 5–8 agents.
+
+Example segmentation for a typical sapcc repo:
+
+| Agent | Packages | Focus |
+|-------|----------|-------|
+| 1 | `cmd/` + `main.go` files | Startup patterns, CLI structure |
+| 2 | `internal/api/` | HTTP handlers, error responses, routing |
+| 3 | `internal/config/` + `internal/auth/` | Configuration, auth patterns |
+| 4 | `internal/storage/` + `internal/wal/` | Storage, persistence, error handling |
+| 5 | `internal/router/` + `internal/source/` | Core logic, concurrency |
+| 6 | `internal/integrity/` + `internal/limiter/` + remaining | Crypto, rate limiting |
+| 7 | All `*_test.go` files | Testing patterns, assertions |
+
+Adjust to actual package sizes.
+
+---
+
+## Additional Discovery Commands
+
+```bash
+# Count .go files per package for sizing agents
+find . -name "*.go" -not -path "./vendor/*" | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn
+
+# List all test files separately (often warrants a dedicated agent)
+find . -name "*_test.go" -not -path "./vendor/*" | sort
+
+# Quick project scale check
+find . -name "*.go" -not -path "./vendor/*" | wc -l
+```
+
+---
+
+## Gate
+
+Packages mapped, agents planned, segmentation table drafted. Proceed to Phase 2.
+
+If more than 30 packages, plan >8 agents. Keep 5–15 files per agent for review depth.
diff --git a/skills/sapcc-audit/references/phase-2-dispatch-agents.md b/skills/sapcc-audit/references/phase-2-dispatch-agents.md
@@ -0,0 +1,148 @@
+# Phase 2: DISPATCH — Agent Dispatch Prompts
+
+> **Load when**: Phase 2 (DISPATCH) begins, after Phase 1 segmentation is complete.
+> **Purpose**: Per-domain agent dispatch prompts for parallel package review.
+
+---
+
+## Dispatch Principles
+
+- **Read the actual code.** Agents MUST use the Read tool to read every .go file in their assigned packages. Read every file directly rather than guessing from names or grep output.
+- **Use gopls MCP tools when available**: `go_workspace` to detect workspace structure, `go_file_context` after reading each .go file for intra-package dependency understanding, `go_symbol_references` to verify type usage across packages (critical for export decisions), `go_package_api` to inspect package APIs, `go_diagnostics` to verify any fixes.
+- **Real review, not checklists.** The primary question for every function is: "Would this pass review?" not "does it follow a checklist." A real reviewer reads code holistically and reacts to architectural issues, not just mechanical patterns.
+- **Segment by package, not by concern.** Dispatch agents by package groups, NOT by concern area. Each agent reviews its packages holistically (errors + architecture + patterns + tests together), exactly like a real PR review.
+- **Code-level findings only.** Every finding MUST include the actual code snippet and a concrete fix showing what it should become.
+
+---
+
+## Standard Dispatch Prompt
+
+Use this prompt verbatim for each dispatched agent, substituting `[list of packages with full paths]`:
+
+```
+You are reviewing code in an SAP Converged Cloud Go project against established
+review standards. Your job is to find things that would actually be commented on
+or rejected in a PR.
+
+PACKAGES TO REVIEW: [list of packages with full paths]
+
+Read EVERY .go file in these packages using the Read tool. For each file:
+
+1. **Over-engineering** (Lead Reviewer's #1 Concern)
+   - Interfaces with only one implementation? → "Just use the concrete type." Project convention: only create interfaces when there are 2+ real implementations.
+   - Wrapper function that adds nothing? → "Delete this, call the real function"
+   - Struct for one-time JSON? → "Use fmt.Sprintf + json.Marshal" (per project convention)
+   - Option struct for constructor? → "Just use positional params." Project convention uses 7-8 positional params, always positional params.
+   - Config file/viper? → "Use osext.MustGetenv." Project convention uses environment variables exclusively. Pure env vars only.
+
+2. **Dead code**
+   - Exported functions with no callers outside the package? Use Grep to check: `grep -r "FunctionName" --include="*.go"`. If no callers exist, flag it.
+   - Interface methods unused
+   - Fields set but unread
+   - Entire packages imported but barely used
+   - "TODO: remove" comments on code that should already be gone
+
+3. **Error messages** (Secondary Reviewer's #1 Concern)
+   - `http.Error(w, "internal error", 500)` — useless to the caller
+   - Error wrapping: uses %w when caller needs errors.Is/As, %s with .Error() to intentionally break chain
+   - Message format: "cannot <operation>: %w" or "while <operation>: %w" with relevant identifiers
+   - Would a user/operator reading this know what to do?
+   - "internal error" with no context = CRITICAL
+   - Return the primary error; log secondary/cleanup errors. Primary error returned, secondary/cleanup errors logged.
+
+4. **Constructor patterns**
+   - Constructor should be `NewX(deps...) *X` — returns infallibly (no error) (construction is infallible)
+   - Uses positional struct literal init: `&API{cfg, ad, fd, sd, ...}` (no field names)
+   - Injects default functions for test doubles: `time.Now`, etc.
+   - Override pattern for test doubles: fluent `OverrideTimeNow(fn) *T` methods
+
+5. **Interface contracts**
+   - If the package implements an interface from another package: Read the interface definition
+   - Check if the implementation actually satisfies the contract
+   - Does it return correct error types? Default values where errors are expected?
+   - Interfaces should be defined in the consumer package, not the implementation package
+
+6. **Copy-paste structs**
+   - Two structs with the same fields (one for internal, one for API response)?
+   - Handler functions that are 90% identical (extract the common pattern)
+   - Duplicated validation logic
+
+7. **HTTP handler patterns** (Must match keppel patterns)
+   - Handlers: methods on *API with `handleVerbResource(w, r)` signature
+   - Auth: called inline at top of handler, NOT middleware
+   - JSON decode: `json.NewDecoder` + `DisallowUnknownFields()`
+   - Responses: `respondwith.JSON(w, status, map[string]any{"key": val})`
+   - Internal errors: `respondwith.ObfuscatedErrorText(w, err)` — hides 500s from clients
+   - Route registration: one `AddTo(*mux.Router)` per API domain, composed via `httpapi.Compose`
+
+8. **Database patterns**
+   - SQL queries as package-level `var` with `sqlext.SimplifyWhitespace()`
+   - PostgreSQL `$1, $2` params (always `$1, $2` (PostgreSQL syntax))
+   - gorp for simple CRUD, raw SQL for complex queries
+   - Transactions: `db.Begin()` + `defer sqlext.RollbackUnlessCommitted(tx)`
+   - NULL: `Option[T]` (from majewsky/gg/option), not `*T` pointers
+
+9. **Type patterns**
+   - Named string types for domain concepts: `type AccountName string`
+   - String enums with typed constants (NOT iota): `const CleanSeverity VulnerabilityStatus = "Clean"`
+   - Model types use `db:"column"` tags; API types use `json:"field"` tags — separate types
+   - Pointer receivers for all struct methods (value receivers only for tiny data-only types)
+
+10. **Logging patterns**
+    - `logg.Fatal` ONLY in cmd/ packages for startup failures
+    - `logg.Error` for secondary/cleanup errors (only for secondary/cleanup errors)
+    - `logg.Info` for operational events
+    - Use logg package for all logging
+    - Panics only for impossible states, annotated with "why was this not caught by Validate!?"
+
+11. **Mixed approaches** (Pattern consistency)
+    - Some handlers return JSON errors, others return text/plain
+    - Some constructors panic on nil args, others return errors
+    - Some packages use logg, others use log
+
+For EACH finding, output:
+
+### [MUST-FIX / SHOULD-FIX / NIT]: [One-line summary]
+**File**: `path/to/file.go:LINE`
+**Convention**: "[What a lead reviewer would actually write in a PR comment]"
+
+**Current code**:
+```go
+[actual code from the file, 3-10 lines]
+```
+
+**Should be**:
+```go
+[what the code should look like after fixing]
+```
+
+**Why**: [One sentence explaining the principle]
+
+---
+
+SEVERITY GUIDE:
+- MUST-FIX: Would block the PR (data loss, interface violation, wrong behavior)
+- SHOULD-FIX: Would get a strong review comment (dead code, copy-paste, bad errors)
+- NIT: Would get a comment but not block (style, naming, minor simplification)
+
+Skip:
+- Generic Go best practices (t.Parallel, DisallowUnknownFields, context.Context first)
+- Things that are actually fine but could theoretically be "better"
+- Suggestions that add complexity without clear benefit
+
+Focus on:
+- Real over-engineering (lead reviewer's #1 concern)
+- Actually useless error messages (secondary reviewer's #1 concern)
+- Dead code that should be deleted
+- Interface contract bugs
+- Constructor/config patterns that diverge from keppel patterns
+- Inconsistent patterns within the same repo
+```
+
+---
+
+## Dispatch Instruction
+
+**Dispatch all agents in a single message using the Task tool with `subagent_type=golang-general-engineer`.**
+
+Gate: All agents dispatched. Proceed to Phase 3.
PATCH

echo "Gold patch applied."
