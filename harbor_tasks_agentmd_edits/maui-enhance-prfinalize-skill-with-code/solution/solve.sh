#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'NEVER use.*--approve.*--request-changes' .github/copilot-instructions.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index f03c3ac15a4d..d258c6022fd8 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -238,10 +238,11 @@ Skills are modular capabilities that can be invoked directly or used by agents.
    - **Categories**: P/0, milestoned, partner, community, recent, docs-maui

 3. **pr-finalize** (`.github/skills/pr-finalize/SKILL.md`)
-   - **Purpose**: Verifies PR title and description match actual implementation. Works on any PR. Optionally updates agent session markdown if present.
+   - **Purpose**: Verifies PR title and description match actual implementation, AND performs code review for best practices before merge.
    - **Trigger phrases**: "finalize PR #XXXXX", "check PR description for #XXXXX", "review commit message"
    - **Used by**: Before merging any PR, when description may be stale
    - **Note**: Does NOT require agent involvement or session markdown - works on any PR
+   - **🚨 CRITICAL**: NEVER use `--approve` or `--request-changes` - only post comments. Approval is a human decision.

 4. **learn-from-pr** (`.github/skills/learn-from-pr/SKILL.md`)
    - **Purpose**: Analyzes completed PR to identify repository improvements (analysis only, no changes applied)
diff --git a/.github/scripts/Review-PR.ps1 b/.github/scripts/Review-PR.ps1
index 250a6eaf20c5..1cdfc8c797c5 100644
--- a/.github/scripts/Review-PR.ps1
+++ b/.github/scripts/Review-PR.ps1
@@ -29,27 +29,31 @@
     If specified, skips merging the PR into the current branch (useful if already merged)

 .PARAMETER Interactive
-    If specified, starts Copilot in interactive mode with the prompt (default).
-    Use -NoInteractive for non-interactive mode that exits after completion.
-
-.PARAMETER NoInteractive
-    If specified, runs in non-interactive mode (exits after completion).
-    Requires --allow-all for tool permissions.
+    If specified, starts Copilot in interactive mode with the prompt.
+    Default is non-interactive mode (exits after completion).

 .PARAMETER DryRun
     If specified, shows what would be done without making changes

+.PARAMETER RunFinalize
+    If specified, runs the pr-finalize skill after the PR agent completes
+    to verify PR title/description match the implementation.
+
+.PARAMETER PostSummaryComment
+    If specified, runs the ai-summary-comment skill after all other phases complete
+    to post a combined summary comment on the PR from all phases.
+
 .EXAMPLE
     .\Review-PR.ps1 -PRNumber 33687
-    Reviews PR #33687 interactively using the default platform (android)
+    Reviews PR #33687 in non-interactive mode (default) using auto-detected platform

 .EXAMPLE
     .\Review-PR.ps1 -PRNumber 33687 -Platform ios -SkipMerge
-    Reviews PR #33687 on iOS without merging (assumes already merged), in interactive mode
+    Reviews PR #33687 on iOS without merging (assumes already merged)

 .EXAMPLE
-    .\Review-PR.ps1 -PRNumber 33687 -NoInteractive
-    Reviews PR #33687 in non-interactive mode (exits after completion)
+    .\Review-PR.ps1 -PRNumber 33687 -Interactive
+    Reviews PR #33687 in interactive mode (stays open for follow-up questions)

 .NOTES
     Prerequisites:
@@ -71,10 +75,16 @@ param(
     [switch]$SkipMerge,

     [Parameter(Mandatory = $false)]
-    [switch]$NoInteractive,
+    [switch]$Interactive,
+
+    [Parameter(Mandatory = $false)]
+    [switch]$DryRun,
+
+    [Parameter(Mandatory = $false)]
+    [switch]$PostSummaryComment,

     [Parameter(Mandatory = $false)]
-    [switch]$DryRun
+    [switch]$RunFinalize
 )

 $ErrorActionPreference = 'Stop'
@@ -230,6 +240,13 @@ Review PR #$PRNumber using the pr agent workflow.

 $platformInstruction

+🚨 **CRITICAL - NEVER MODIFY GIT STATE:**
+- NEVER run ``git checkout``, ``git switch``, ``git fetch``, ``git stash``, or ``git reset``
+- NEVER run ``git push`` - you do NOT have permission to push anything
+- You are ALWAYS on the correct branch already - the script handles this
+- If the state file says "wrong branch", that's stale state - delete it and start fresh
+- If you think you need to switch branches or push changes, you are WRONG - ask the user instead
+
 **Instructions:**
 1. Read the plan template at ``$planTemplatePath`` for the 5-phase workflow
 2. Read ``.github/agents/pr.md`` for Phases 1-3 instructions
@@ -254,7 +271,7 @@ if ($DryRun) {
     Write-Host "[DRY RUN] Would invoke Copilot CLI with:" -ForegroundColor Magenta
     Write-Host ""
     Write-Host "  Agent: pr" -ForegroundColor Gray
-    Write-Host "  Mode: $(if ($NoInteractive) { 'Non-interactive (-p)' } else { 'Interactive (-i)' })" -ForegroundColor Gray
+    Write-Host "  Mode: $(if ($Interactive) { 'Interactive (-i)' } else { 'Non-interactive (-p)' })" -ForegroundColor Gray
     Write-Host "  PR: #$PRNumber" -ForegroundColor Gray
     Write-Host "  Platform: $(if ($Platform) { $Platform } else { '(agent will determine)' })" -ForegroundColor Gray
     Write-Host ""
@@ -264,7 +281,7 @@ if ($DryRun) {
     Write-Host "To run for real, remove the -DryRun flag" -ForegroundColor Yellow
 } else {
     Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
-    Write-Host "║  LAUNCHING COPILOT CLI                                    ║" -ForegroundColor Green
+    Write-Host "║  PHASE 1: PR AGENT REVIEW                                 ║" -ForegroundColor Green
     Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
     Write-Host ""
     Write-Host "PR Review Context:" -ForegroundColor Cyan
@@ -274,7 +291,16 @@ if ($DryRun) {
     Write-Host "  PLAN_TEMPLATE:  $planTemplatePath" -ForegroundColor White
     Write-Host "  CURRENT_BRANCH: $(git branch --show-current)" -ForegroundColor White
     Write-Host "  PR_TITLE:       $($prInfo.title)" -ForegroundColor White
-    Write-Host "  MODE:           $(if ($NoInteractive) { 'Non-interactive' } else { 'Interactive' })" -ForegroundColor White
+    Write-Host "  MODE:           $(if ($Interactive) { 'Interactive' } else { 'Non-interactive' })" -ForegroundColor White
+    Write-Host ""
+    Write-Host "Workflow:" -ForegroundColor Cyan
+    Write-Host "  1. PR Agent Review (this phase)" -ForegroundColor White
+    if ($RunFinalize) {
+        Write-Host "  2. pr-finalize skill (queued)" -ForegroundColor White
+    }
+    if ($PostSummaryComment) {
+        Write-Host "  3. ai-summary-comment skill (queued)" -ForegroundColor White
+    }
     Write-Host ""
     Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
     Write-Host ""
@@ -297,14 +323,14 @@ if ($DryRun) {
     # Add logging options
     $copilotArgs += @("--log-dir", $prLogDir, "--log-level", "info")

-    if ($NoInteractive) {
-        # Non-interactive mode: -p with --allow-all
+    if ($Interactive) {
+        # Interactive mode: -i to start with prompt
+        $copilotArgs += @("-i", $prompt)
+    } else {
+        # Non-interactive mode (default): -p with --allow-all
         # Also save session to markdown for review
         $sessionFile = Join-Path $prLogDir "session-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
         $copilotArgs += @("-p", $prompt, "--allow-all", "--share", $sessionFile)
-    } else {
-        # Interactive mode: -i to start with prompt
-        $copilotArgs += @("-i", $prompt)
     }

     Write-Host "🚀 Starting Copilot CLI..." -ForegroundColor Yellow
@@ -322,6 +348,64 @@ if ($DryRun) {
     } else {
         Write-Host "⚠️ Copilot CLI exited with code: $exitCode" -ForegroundColor Yellow
     }
+
+    # Post-completion skills (only run if main agent completed successfully)
+    if ($exitCode -eq 0) {
+
+        # Phase 2: Run pr-finalize skill if requested
+        if ($RunFinalize) {
+            Write-Host ""
+            Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
+            Write-Host "║  PHASE 2: PR-FINALIZE SKILL                               ║" -ForegroundColor Magenta
+            Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
+            Write-Host ""
+
+            $finalizePrompt = "Run the pr-finalize skill for PR #$PRNumber. Verify the PR title and description match the actual implementation. Do NOT post a comment - just update the state file at CustomAgentLogsTmp/PRState/pr-$PRNumber.md with your findings."
+
+            $finalizeArgs = @(
+                "-p", $finalizePrompt,
+                "--allow-all",
+                "--stream", "on"
+            )
+
+            Write-Host "🔍 Running pr-finalize..." -ForegroundColor Yellow
+            & copilot @finalizeArgs
+
+            $finalizeExit = $LASTEXITCODE
+            if ($finalizeExit -eq 0) {
+                Write-Host "✅ pr-finalize completed" -ForegroundColor Green
+            } else {
+                Write-Host "⚠️ pr-finalize exited with code: $finalizeExit" -ForegroundColor Yellow
+            }
+        }
+
+        # Phase 3: Run ai-summary-comment skill if requested (posts combined results)
+        if ($PostSummaryComment) {
+            Write-Host ""
+            Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
+            Write-Host "║  PHASE 3: POST SUMMARY COMMENT                            ║" -ForegroundColor Magenta
+            Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
+            Write-Host ""
+
+            $commentPrompt = "Use the ai-summary-comment skill to post a comment on PR #$PRNumber based on the results from the PR agent review and pr-finalize phases in CustomAgentLogsTmp/PRState/pr-$PRNumber.md."
+
+            $commentArgs = @(
+                "-p", $commentPrompt,
+                "--allow-all",
+                "--stream", "on"
+            )
+
+            Write-Host "💬 Posting summary comment..." -ForegroundColor Yellow
+            & copilot @commentArgs
+
+            $commentExit = $LASTEXITCODE
+            if ($commentExit -eq 0) {
+                Write-Host "✅ Summary comment posted" -ForegroundColor Green
+            } else {
+                Write-Host "⚠️ ai-summary-comment exited with code: $commentExit" -ForegroundColor Yellow
+            }
+        }
+    }
 }

 Write-Host ""
@@ -329,7 +413,7 @@ Write-Host "📝 State file: CustomAgentLogsTmp/PRState/pr-$PRNumber.md" -Foregr
 Write-Host "📋 Plan template: $planTemplatePath" -ForegroundColor Gray
 if (-not $DryRun) {
     Write-Host "📁 Copilot logs: CustomAgentLogsTmp/PRState/$PRNumber/copilot-logs/" -ForegroundColor Gray
-    if ($NoInteractive) {
+    if (-not $Interactive) {
         Write-Host "📄 Session markdown: $sessionFile" -ForegroundColor Gray
     }
 }
diff --git a/.github/skills/ai-summary-comment/SKILL.md b/.github/skills/ai-summary-comment/SKILL.md
index a5ee581267c2..049918f02a17 100644
--- a/.github/skills/ai-summary-comment/SKILL.md
+++ b/.github/skills/ai-summary-comment/SKILL.md
@@ -56,11 +56,17 @@ Most scripts post to the **same single comment** identified by `<!-- AI Summary

 ### Separate PR Finalization Comment

-The `post-pr-finalize-comment.ps1` script posts a **separate comment** identified by `<!-- PR-FINALIZE-COMMENT -->`. This comment contains two sections:
-- **Title**: Shows the suggested PR title with comparison to current
-- **Description**: Shows the suggested PR description
+The `post-pr-finalize-comment.ps1` script posts a **separate comment** identified by `<!-- PR-FINALIZE-COMMENT -->`. This comment contains three sections:
+- **Title**: Shows the current vs recommended PR title
+- **Description**: Shows description assessment, missing elements, and **recommended description**
+- **Code Review**: Shows code review findings (critical issues, suggestions, positive observations)

-If an existing finalize comment exists, it will be replaced with the updated Title and Description sections. This keeps finalization reviews distinct from automated analysis.
+If an existing finalize comment exists, it will be replaced with the updated sections. This keeps finalization reviews distinct from automated analysis.
+
+**⚠️ Important Requirements for PR Finalize Comments:**
+- When `TitleStatus` is `NeedsUpdate`, **always provide** `-RecommendedTitle`
+- When `DescriptionStatus` is `NeedsUpdate` or `NeedsRewrite`, **always provide** `-RecommendedDescription` with the full suggested description text
+- The script will warn if these are missing but won't fail

 ## Section Scripts

@@ -449,6 +455,101 @@ CustomAgentLogsTmp/PRState/{IssueNumber}/write-tests/

 ---

+## PR Finalize Comment Script
+
+The `post-pr-finalize-comment.ps1` script posts a **separate comment** (not part of the unified AI Summary) specifically for PR finalization reviews. It provides structured feedback on the PR title, description, and code review findings.
+
+### Usage
+
+#### Simplest: Just provide PR number (auto-loads from summary file)
+
+```powershell
+# Auto-loads from CustomAgentLogsTmp/PRState/{PRNumber}/pr-finalize/pr-finalize-summary.md
+pwsh .github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 -PRNumber 33892
+```
+
+#### Full manual parameters (recommended for best results)
+
+```powershell
+pwsh .github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 `
+    -PRNumber 33892 `
+    -TitleStatus "NeedsUpdate" `
+    -CurrentTitle "Fix 32650 Image Orientation" `
+    -RecommendedTitle "[iOS][Android] MediaPicker: Fix image orientation when RotateImage=true" `
+    -TitleIssues "- Missing platform tags
+- Doesn't describe the behavior fix" `
+    -DescriptionStatus "NeedsUpdate" `
+    -DescriptionAssessment "The current description is minimal and missing:
+- ❌ Missing NOTE block for testing artifacts
+- ❌ No root cause analysis
+- ❌ No technical details" `
+    -MissingElements "Add the NOTE block, root cause, and technical details." `
+    -RecommendedDescription "> [!NOTE]
+> Are you waiting for this PR? Test it: [Testing PR Builds](link)
+
+### Root Cause
+...description...
+
+### Description of Change
+...details..." `
+    -CodeReviewStatus "IssuesFound" `
+    -CodeReviewFindings "### 🔴 Critical Issues
+**1. Broken indentation**
+- File: \`src/file.cs\`
+- Problem: Inconsistent tabs/spaces
+
+### 🟡 Suggestions
+1. Consider disposing Matrix object
+
+### ✅ Looks Good
+- Proper cleanup in finally block"
+```
+
+### Parameters
+
+| Parameter | Required | Description |
+|-----------|----------|-------------|
+| `PRNumber` | Yes* | Pull request number |
+| `SummaryFile` | No | Path to pr-finalize-summary.md (auto-discovered) |
+| `TitleStatus` | No* | `Good` or `NeedsUpdate` |
+| `CurrentTitle` | No* | Current PR title (fetched from GitHub if not provided) |
+| `RecommendedTitle` | No | **Required if TitleStatus is NeedsUpdate** |
+| `TitleIssues` | No | List of issues with current title |
+| `DescriptionStatus` | No* | `Excellent`, `Good`, `NeedsUpdate`, or `NeedsRewrite` |
+| `DescriptionAssessment` | Yes | Assessment of description quality |
+| `MissingElements` | No | What's missing from the description |
+| `RecommendedDescription` | No | **Required if DescriptionStatus is NeedsUpdate/NeedsRewrite** |
+| `CodeReviewStatus` | No | `Passed`, `IssuesFound`, or `Skipped` |
+| `CodeReviewFindings` | No | Markdown content for code review section |
+| `DryRun` | No | Preview instead of posting |
+
+*At least PRNumber or SummaryFile required. Script auto-detects values when possible.
+
+### ⚠️ Common Mistakes to Avoid
+
+1. **Missing RecommendedTitle when TitleStatus is NeedsUpdate**
+   - The script will warn but still post - always provide a recommended title
+
+2. **Missing RecommendedDescription when DescriptionStatus is NeedsUpdate**
+   - Users need to see what the description SHOULD look like
+
+3. **Code review findings not starting with proper headers**
+   - Always structure with `### 🔴 Critical Issues`, `### 🟡 Suggestions`, `### ✅ Looks Good`
+
+4. **Auto-parsing from summary file getting confused**
+   - When in doubt, provide explicit parameters instead of relying on auto-parsing
+
+### Expected Directory Structure for Auto-Loading
+
+```
+CustomAgentLogsTmp/PRState/{PRNumber}/pr-finalize/
+├── pr-finalize-summary.md      # Main summary (auto-parsed)
+├── recommended-description.md  # Full recommended description (optional)
+└── code-review.md             # Code review findings (optional)
+```
+
+---
+
 ## Technical Details

 - Comments identified by HTML marker `<!-- AI Summary -->`
diff --git a/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 b/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
index 0cfcf8928bb2..f3d889b51f69 100644
--- a/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
+++ b/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
@@ -4,7 +4,7 @@
     Posts or updates a PR finalize comment on a GitHub Pull Request.

 .DESCRIPTION
-    Creates ONE comment for PR finalization with two collapsible sections: Title and Description.
+    Creates ONE comment for PR finalization with three collapsible sections: Title, Description, and Code Review.
     Uses HTML marker <!-- PR-FINALIZE-COMMENT --> for identification.

     **Auto-loads from CustomAgentLogsTmp/PRState/{PRNumber}/pr-finalize/**
@@ -25,6 +25,11 @@
     <summary><b>Description: ⚠️ Needs Update</b></summary>
     ... description details ...
     </details>
+
+    <details>
+    <summary><b>Code Review: ✅ Passed</b></summary>
+    ... code review findings ...
+    </details>

 .PARAMETER PRNumber
     The PR number to post comment on (required unless SummaryFile provided)
@@ -56,6 +61,12 @@
 .PARAMETER RecommendedDescription
     Full recommended description (optional - only if needs rewrite)

+.PARAMETER CodeReviewStatus
+    Code review assessment: "Passed", "IssuesFound", "Skipped" (optional - defaults to "Skipped" if not provided)
+
+.PARAMETER CodeReviewFindings
+    Code review findings content (optional - markdown with critical issues, suggestions, and positive observations)
+
 .PARAMETER DryRun
     Print comment instead of posting

@@ -73,7 +84,9 @@
         -TitleStatus "Good" `
         -CurrentTitle "[iOS] Fix SafeArea padding calculation" `
         -DescriptionStatus "Good" `
-        -DescriptionAssessment "Clear structure, accurate technical details, matches implementation"
+        -DescriptionAssessment "Clear structure, accurate technical details, matches implementation" `
+        -CodeReviewStatus "Passed" `
+        -CodeReviewFindings "No critical issues found. Code follows best practices."
 #>

 param(
@@ -109,6 +122,13 @@ param(
     [Parameter(Mandatory=$false)]
     [string]$RecommendedDescription,

+    [Parameter(Mandatory=$false)]
+    [ValidateSet("Passed", "IssuesFound", "Skipped", "")]
+    [string]$CodeReviewStatus,
+
+    [Parameter(Mandatory=$false)]
+    [string]$CodeReviewFindings,
+
     [Parameter(Mandatory=$false)]
     [switch]$DryRun,

@@ -127,7 +147,7 @@ Write-Host "╚═════════════════════
 # ============================================================================

 # If PRNumber provided but no SummaryFile, try to find it
-if ($PRNumber -gt 0 -and [string]::IsNullOrWhiteSpace($SummaryFile) -and [string]::IsNullOrWhiteSpace($ReviewDescription)) {
+if ($PRNumber -gt 0 -and [string]::IsNullOrWhiteSpace($SummaryFile)) {
     $summaryPath = "CustomAgentLogsTmp/PRState/$PRNumber/pr-finalize/pr-finalize-summary.md"
     if (-not (Test-Path $summaryPath)) {
         $repoRoot = git rev-parse --show-toplevel 2>$null
@@ -157,10 +177,32 @@ if (-not [string]::IsNullOrWhiteSpace($SummaryFile)) {
         Write-Host "ℹ️  Auto-detected PRNumber: $PRNumber from path" -ForegroundColor Cyan
     }

-    # Extract Title assessment
+    # Extract Recommended Title FIRST (needed for TitleStatus detection)
+    if ([string]::IsNullOrWhiteSpace($RecommendedTitle)) {
+        # Try different patterns
+        if ($content -match '\*\*Recommended.*?Title.*?\*\*:?\s*[`"]?([^`"\n]+)[`"]?') {
+            $RecommendedTitle = $Matches[1].Trim()
+        } elseif ($content -match 'Recommended:\s*`([^`]+)`') {
+            $RecommendedTitle = $Matches[1].Trim()
+        } elseif ($content -match '(?s)\*\*Recommended:\*\*\s*```\s*([^\n]+)') {
+            # Code fence format
+            $RecommendedTitle = $Matches[1].Trim()
+        } elseif ($content -match '(?s)### 📋 Title Assessment.+?\*\*Recommended:\*\*\s*```\s*([^\n]+)') {
+            $RecommendedTitle = $Matches[1].Trim()
+        }
+        if ($RecommendedTitle) {
+            Write-Host "ℹ️  Extracted RecommendedTitle: $RecommendedTitle" -ForegroundColor Cyan
+        }
+    }
+
+    # Extract Title assessment - if RecommendedTitle exists, title needs update
     if ([string]::IsNullOrWhiteSpace($TitleStatus)) {
+        # If we have a recommended title, the title needs update
+        if (-not [string]::IsNullOrWhiteSpace($RecommendedTitle)) {
+            $TitleStatus = "NeedsUpdate"
+        }
         # Look for explicit status in Title Assessment section
-        if ($content -match '(?s)### 📋 Title Assessment.+?\*\*Status:\*\*\s*(✅|❌|⚠️)?\s*(Good|NeedsUpdate|Needs Update)') {
+        elseif ($content -match '(?s)### 📋 Title Assessment.+?\*\*Status:\*\*\s*(✅|❌|⚠️)?\s*(Good|NeedsUpdate|Needs Update)') {
             $statusMatch = $Matches[2] -replace '\s+', ''
             if ($statusMatch -eq "Good") {
                 $TitleStatus = "Good"
@@ -189,24 +231,6 @@ if (-not [string]::IsNullOrWhiteSpace($SummaryFile)) {
         }
     }

-    # Extract Recommended Title
-    if ([string]::IsNullOrWhiteSpace($RecommendedTitle)) {
-        # Try different patterns
-        if ($content -match '\*\*Recommended.*?Title.*?\*\*:?\s*[`"]?([^`"\n]+)[`"]?') {
-            $RecommendedTitle = $Matches[1].Trim()
-        } elseif ($content -match 'Recommended:\s*`([^`]+)`') {
-            $RecommendedTitle = $Matches[1].Trim()
-        } elseif ($content -match '(?s)\*\*Recommended:\*\*\s*```\s*([^\n]+)') {
-            # Code fence format
-            $RecommendedTitle = $Matches[1].Trim()
-        } elseif ($content -match '(?s)### 📋 Title Assessment.+?\*\*Recommended:\*\*\s*```\s*([^\n]+)') {
-            $RecommendedTitle = $Matches[1].Trim()
-        }
-        if ($RecommendedTitle) {
-            Write-Host "ℹ️  Extracted RecommendedTitle: $RecommendedTitle" -ForegroundColor Cyan
-        }
-    }
-
     # Extract Description assessment
     if ([string]::IsNullOrWhiteSpace($DescriptionStatus)) {
         if ($content -match 'Description.*?Excellent|Excellent.*?description') {
@@ -308,6 +332,57 @@ if (-not [string]::IsNullOrWhiteSpace($SummaryFile)) {
             $RecommendedDescription = $Matches[1].Trim()
         }
     }
+
+    # Extract Code Review Status and Findings
+    if ([string]::IsNullOrWhiteSpace($CodeReviewStatus)) {
+        # First, try to find a separate code-review.md file in same directory
+        $summaryDir = Split-Path $SummaryFile -Parent
+        $codeReviewFile = Join-Path $summaryDir "code-review.md"
+
+        if (Test-Path $codeReviewFile) {
+            Write-Host "ℹ️  Found code-review.md file, loading content..." -ForegroundColor Cyan
+            $codeReviewContent = Get-Content $codeReviewFile -Raw -Encoding UTF8
+            $CodeReviewFindings = $codeReviewContent.Trim()
+
+            # Determine status from content
+            if ($codeReviewContent -match '🔴 Critical Issues') {
+                $CodeReviewStatus = "IssuesFound"
+            } elseif ($codeReviewContent -match '(✅ Looks Good|No.*?issues found|Code review passed)') {
+                $CodeReviewStatus = "Passed"
+            } else {
+                $CodeReviewStatus = "Passed"
+            }
+        }
+        # Try to extract from summary file - look for Code Review section
+        elseif ($content -match '(?s)## Code Review Findings(.+?)(?=## [A-Z]|---|\z)') {
+            Write-Host "ℹ️  Extracted code review from summary file..." -ForegroundColor Cyan
+            $CodeReviewFindings = $Matches[1].Trim()
+
+            # Determine status from content
+            if ($CodeReviewFindings -match '🔴 Critical Issues') {
+                $CodeReviewStatus = "IssuesFound"
+            } else {
+                $CodeReviewStatus = "Passed"
+            }
+        }
+        # Also check for ### Code Review format
+        elseif ($content -match '(?s)### 🔍 Code Review(.+?)(?=### [A-Z]|---|\z)') {
+            $CodeReviewFindings = $Matches[1].Trim()
+            if ($CodeReviewFindings -match '🔴 Critical Issues') {
+                $CodeReviewStatus = "IssuesFound"
+            } else {
+                $CodeReviewStatus = "Passed"
+            }
+        }
+        else {
+            # Default to Skipped if no code review found
+            $CodeReviewStatus = "Skipped"
+        }
+
+        if ($CodeReviewStatus -ne "Skipped") {
+            Write-Host "ℹ️  Detected CodeReviewStatus: $CodeReviewStatus" -ForegroundColor Cyan
+        }
+    }
 }

 # Validate required parameters
@@ -338,6 +413,18 @@ if ([string]::IsNullOrWhiteSpace($DescriptionAssessment)) {
     throw "DescriptionAssessment is required. Provide via -DescriptionAssessment or use -SummaryFile"
 }

+# Warn if description needs work but no recommended description is provided
+if (($DescriptionStatus -eq "NeedsUpdate" -or $DescriptionStatus -eq "NeedsRewrite") -and [string]::IsNullOrWhiteSpace($RecommendedDescription)) {
+    Write-Host "⚠️  Warning: DescriptionStatus is '$DescriptionStatus' but no RecommendedDescription provided." -ForegroundColor Yellow
+    Write-Host "   Consider providing -RecommendedDescription with a suggested PR description." -ForegroundColor Yellow
+}
+
+# Warn if title needs update but no recommended title is provided
+if ($TitleStatus -eq "NeedsUpdate" -and [string]::IsNullOrWhiteSpace($RecommendedTitle)) {
+    Write-Host "⚠️  Warning: TitleStatus is 'NeedsUpdate' but no RecommendedTitle provided." -ForegroundColor Yellow
+    Write-Host "   Consider providing -RecommendedTitle with a suggested title." -ForegroundColor Yellow
+}
+
 # Initialize $titleIssues from parameter if provided, otherwise set default based on status
 if (-not (Get-Variable -Name 'titleIssues' -ErrorAction SilentlyContinue) -or [string]::IsNullOrWhiteSpace($titleIssues)) {
     if (-not [string]::IsNullOrWhiteSpace($TitleIssues)) {
@@ -379,6 +466,7 @@ $descStatusDisplay = switch ($DescriptionStatus) {
 # Build Title section (collapsible)
 $titleSection = @"
 <details>
+
 <summary><b>Title: $titleEmoji $titleStatusDisplay</b></summary>

 <br>
@@ -406,6 +494,7 @@ $titleSection += @"
 # Build Description section (collapsible)
 $descSection = @"
 <details>
+
 <summary><b>Description: $descEmoji $descStatusDisplay</b></summary>

 <br>
@@ -436,6 +525,51 @@ $descSection += @"
 </details>
 "@

+# Code Review status emoji and display
+$codeReviewEmoji = switch ($CodeReviewStatus) {
+    "Passed" { "✅" }
+    "IssuesFound" { "⚠️" }
+    "Skipped" { "⏭️" }
+    default { "⏭️" }
+}
+
+$codeReviewStatusDisplay = switch ($CodeReviewStatus) {
+    "IssuesFound" { "Issues Found" }
+    default { $CodeReviewStatus }
+}
+
+# Build Code Review section (collapsible) - only if not skipped or if we have findings
+$codeReviewSection = ""
+if ($CodeReviewStatus -ne "Skipped" -or -not [string]::IsNullOrWhiteSpace($CodeReviewFindings)) {
+    # Default status to "Passed" if we have findings but no explicit status
+    if ([string]::IsNullOrWhiteSpace($CodeReviewStatus)) {
+        $CodeReviewStatus = "Passed"
+        $codeReviewEmoji = "✅"
+        $codeReviewStatusDisplay = "Passed"
+    }
+
+    $codeReviewSection = @"
+
+<details>
+
+<summary><b>Code Review: $codeReviewEmoji $codeReviewStatusDisplay</b></summary>
+
+"@
+
+    if (-not [string]::IsNullOrWhiteSpace($CodeReviewFindings)) {
+        # Trim the findings and ensure proper newline spacing
+        $trimmedFindings = $CodeReviewFindings.Trim()
+        $codeReviewSection += "`n$trimmedFindings"
+    } else {
+        $codeReviewSection += "`nNo significant issues found. Code follows best practices."
+    }
+
+    $codeReviewSection += @"
+
+</details>
+"@
+}
+
 # ============================================================================
 # STANDALONE COMMENT HANDLING
 # Posts as separate PR Finalization comment with marker
@@ -473,6 +607,7 @@ $FINALIZE_MARKER
 $titleSection

 $descSection
+$codeReviewSection
 "@

 if ($DryRun) {
diff --git a/.github/skills/pr-finalize/SKILL.md b/.github/skills/pr-finalize/SKILL.md
index d99df5da8e72..c1c8af7144de 100644
--- a/.github/skills/pr-finalize/SKILL.md
+++ b/.github/skills/pr-finalize/SKILL.md
@@ -1,15 +1,53 @@
 ---
 name: pr-finalize
-description: Finalizes any PR for merge by verifying title and description match actual implementation. Reviews existing description quality before suggesting changes. Use when asked to "finalize PR", "check PR description", "review commit message", before merging any PR, or when PR implementation changed during review. Do NOT use for extracting lessons (use learn-from-pr), writing tests (use write-tests-agent), or investigating build failures (use pr-build-status).
+description: Finalizes any PR for merge by verifying title/description match implementation AND performing code review for best practices. Use when asked to "finalize PR", "check PR description", "review commit message", before merging any PR, or when PR implementation changed during review. Do NOT use for extracting lessons (use learn-from-pr), writing tests (use write-tests-agent), or investigating build failures (use pr-build-status).
 ---

 # PR Finalize

-Ensures PR title and description accurately reflect the implementation for a good commit message.
+Ensures PR title and description accurately reflect the implementation, and performs a **code review** for best practices before merge.

 **Standalone skill** - Can be used on any PR, not just PRs created by the pr agent.

-## Core Principle: Preserve Quality
+## Two-Phase Workflow
+
+1. **Title & Description Review** - Verify PR metadata matches implementation
+2. **Code Review** - Review code for best practices and potential issues
+
+---
+
+## 🚨 CRITICAL RULES
+
+### 1. NEVER Approve or Request Changes
+
+**AI agents must NEVER use `--approve` or `--request-changes` flags.**
+
+| Action | Allowed? | Why |
+|--------|----------|-----|
+| `gh pr review --approve` | ❌ **NEVER** | Approval is a human decision |
+| `gh pr review --request-changes` | ❌ **NEVER** | Blocking PRs is a human decision |
+
+### 2. NEVER Post Comments Directly
+
+**This skill is ANALYSIS ONLY.** Never post comments using `gh` commands.
+
+| Action | Allowed? | Why |
+|--------|----------|-----|
+| `gh pr review --comment` | ❌ **NEVER** | Use ai-summary-comment skill instead |
+| `gh pr comment` | ❌ **NEVER** | Use ai-summary-comment skill instead |
+| Analyze and report findings | ✅ **YES** | This is the skill's purpose |
+
+**Correct workflow:**
+1. **This skill**: Analyze PR, produce findings in your response to the user
+2. **User explicitly asks to post comment**: Then invoke `ai-summary-comment` skill
+
+**Only humans control when comments are posted.** Your job is to analyze and present findings.
+
+---
+
+## Phase 1: Title & Description
+
+### Core Principle: Preserve Quality

 **Review existing description BEFORE suggesting changes.** Many PR authors write excellent, detailed descriptions. Your job is to:

@@ -278,6 +316,73 @@ Fixed the issue mentioned in #30897

 **Verdict:** Inadequate - no detail on what changed. Use template.

+---
+
+## Phase 2: Code Review
+
+After verifying title/description, perform a **code review** to catch best practice violations and potential issues before merge.
+
+### Review Focus Areas
+
+When reviewing code changes, focus on:
+
+1. **Code quality and maintainability** - Clean code, good naming, appropriate abstractions
+2. **Error handling and edge cases** - Null checks, exception handling, boundary conditions
+3. **Performance implications** - Unnecessary allocations, N+1 queries, blocking calls
+4. **Platform-specific concerns** - iOS/Android/Windows differences, platform APIs
+5. **Breaking changes** - API changes, behavior changes that affect existing code
+
+### How to Review
+
+```bash
+# Get the PR diff
+gh pr diff XXXXX
+
+# Review specific files
+gh pr diff XXXXX -- path/to/file.cs
+```
+
+### Output Format
+
+```markdown
+## Code Review Findings
+
+### 🔴 Critical Issues
+
+**[Issue Title]**
+- **File:** [path/to/file.cs]
+- **Problem:** [Description]
+- **Recommendation:** [Code fix or approach]
+
+### 🟡 Suggestions
+
+- [Suggestion 1]
+- [Suggestion 2]
+
+### ✅ Looks Good
+
+- [Positive observation 1]
+- [Positive observation 2]
+```
+
+### 🚨 CRITICAL: Do NOT Post Comments Directly
+
+**The pr-finalize skill is ANALYSIS ONLY.** Never post comments using `gh pr review` or `gh pr comment`.
+
+| Action | Allowed? | Why |
+|--------|----------|-----|
+| `gh pr review --comment` | ❌ **NEVER** | Use ai-summary-comment skill instead |
+| `gh pr comment` | ❌ **NEVER** | Use ai-summary-comment skill instead |
+| Analyze and report findings | ✅ **YES** | This is the skill's purpose |
+
+**Workflow:**
+1. **This skill**: Analyze PR, produce findings in your response
+2. **User asks to post**: Then invoke `ai-summary-comment` skill to post
+
+The user controls when comments are posted. Your job is to analyze and present findings.
+
+---
+
 ## Complete Example

 See [references/complete-example.md](references/complete-example.md) for a full agent-optimized PR description showing all elements above applied to a real SafeArea fix.

PATCH

echo "Patch applied successfully."
