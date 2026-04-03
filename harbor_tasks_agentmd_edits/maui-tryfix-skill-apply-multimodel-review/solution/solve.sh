#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'existingTryFixPreview' .github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1 b/.github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1
index 5c3d5634b1dc..43d8a2fdc5ab 100644
--- a/.github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1
+++ b/.github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1
@@ -410,9 +410,31 @@ if ($DryRun) {
     $TRY_FIX_END_MARKER = "<!-- /SECTION:TRY-FIX -->"

     if ($existingPreview -match [regex]::Escape($TRY_FIX_MARKER)) {
-        # Replace existing TRY-FIX section
+        # Extract existing TRY-FIX content to preserve previous attempts (same logic as GitHub comment path)
+        $startPattern = [regex]::Escape($TRY_FIX_MARKER)
+        $endPattern = [regex]::Escape($TRY_FIX_END_MARKER)
+        $existingTryFixPreview = ""
+        if ($existingPreview -match "(?s)$startPattern(.*?)$endPattern") {
+            $existingTryFixPreview = $Matches[1].Trim()
+        }
+
+        # Check if this attempt already exists - replace it, otherwise append
+        $attemptPatternPreview = "(?s)<details>\s*<summary>.*?(Attempt $AttemptNumber`:|Fix $AttemptNumber).*?</details>"
+        if ($existingTryFixPreview -match $attemptPatternPreview) {
+            Write-Host "Replacing existing Fix $AttemptNumber in preview..." -ForegroundColor Yellow
+            $updatedTryFixContent = $existingTryFixPreview -replace $attemptPatternPreview, $attemptSection
+            $tryFixSectionUpdated = "$SECTION_START`n$tryFixHeader$updatedTryFixContent`n$SECTION_END"
+        } else {
+            Write-Host "Adding Fix $AttemptNumber to preview..." -ForegroundColor Yellow
+            # Remove header if present to avoid duplication
+            $existingTryFixPreview = $existingTryFixPreview -replace "^### \ud83d\udd27 (Try-Fix Analysis|Fix Attempts)\s*`n*", ""
+            $updatedTryFixContent = $tryFixHeader + $existingTryFixPreview.TrimEnd() + "`n`n" + $attemptSection
+            $tryFixSectionUpdated = "$SECTION_START`n$updatedTryFixContent`n$SECTION_END"
+        }
+
+        # Replace the section in the preview
         $pattern = [regex]::Escape($TRY_FIX_MARKER) + "[\s\S]*?" + [regex]::Escape($TRY_FIX_END_MARKER)
-        $finalComment = $existingPreview -replace $pattern, $tryFixSection
+        $finalComment = $existingPreview -replace $pattern, $tryFixSectionUpdated
     } elseif (-not [string]::IsNullOrWhiteSpace($existingPreview)) {
         # Append TRY-FIX section to existing content
         $finalComment = $existingPreview.TrimEnd() + "`n`n" + $tryFixSection
diff --git a/.github/skills/try-fix/SKILL.md b/.github/skills/try-fix/SKILL.md
index 77459f11e13f..0fd1188c7fa2 100644
--- a/.github/skills/try-fix/SKILL.md
+++ b/.github/skills/try-fix/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: try-fix
 description: Attempts ONE alternative fix for a bug, tests it empirically, and reports results. ALWAYS explores a DIFFERENT approach from existing PR fixes. Use when CI or an agent needs to try independent fix alternatives. Invoke with problem description, test command, target files, and optional hints.
+compatibility: Requires PowerShell, git, .NET MAUI build environment, Android/iOS device or emulator
 ---

 # Try Fix Skill
@@ -17,6 +18,23 @@ Attempts ONE fix for a given problem. Receives all context upfront, tries a sing

 **Every invocation:** Review existing fixes → Think of DIFFERENT approach → Implement and test → Report results

+## ⚠️ CRITICAL: Sequential Execution Only
+
+🚨 **Try-fix runs MUST be executed ONE AT A TIME - NEVER in parallel.**
+
+**Why:** Each try-fix run:
+- Modifies the same source files (SafeAreaExtensions.cs, etc.)
+- Uses the same device/emulator for testing
+- Runs EstablishBrokenBaseline.ps1 which reverts files to a known state
+
+**If run in parallel:**
+- Multiple agents will overwrite each other's code changes
+- Device tests will interfere with each other
+- Baseline script will conflict, causing unpredictable file states
+- Results will be corrupted and unreliable
+
+**Correct pattern:** Run attempt-1, wait for completion, then run attempt-2, etc.
+
 ## Inputs

 All inputs are provided by the invoker (CI, agent, or user).
@@ -39,15 +57,57 @@ Results reported back to the invoker:
 |-------|-------------|
 | `approach` | What fix was attempted (brief description) |
 | `files_changed` | Which files were modified |
-| `result` | `PASS` or `FAIL` |
+| `result` | `Pass`, `Fail`, or `Blocked` |
 | `analysis` | Why it worked, or why it failed and what was learned |
 | `diff` | The actual code changes made (for review) |

-## Output Structure
+## Output Structure (MANDATORY)
+
+**FIRST STEP: Create output directory before doing anything else.**
+
+```powershell
+# Set issue/PR number explicitly (from branch name, PR context, or manual input)
+$IssueNumber = "<ISSUE_OR_PR_NUMBER>"  # Replace with actual number
+
+# Find next attempt number
+$tryFixDir = "CustomAgentLogsTmp/PRState/$IssueNumber/try-fix"
+$existingAttempts = (Get-ChildItem "$tryFixDir/attempt-*" -Directory -ErrorAction SilentlyContinue).Count
+$attemptNum = $existingAttempts + 1
+
+# Create output directory
+$OUTPUT_DIR = "$tryFixDir/attempt-$attemptNum"
+New-Item -ItemType Directory -Path $OUTPUT_DIR -Force | Out-Null
+
+Write-Host "Output directory: $OUTPUT_DIR"
+```
+
+**Required files to create in `$OUTPUT_DIR`:**
+
+| File | When to Create | Content |
+|------|----------------|---------|
+| `baseline.log` | After Step 2 (Baseline) | Output from EstablishBrokenBaseline.ps1 proving baseline was established |
+| `approach.md` | After Step 4 (Design) | What fix you're attempting and why it's different from existing fixes |
+| `result.txt` | After Step 6 (Test) | Single word: `Pass`, `Fail`, or `Blocked` |
+| `fix.diff` | After Step 6 (Test) | Output of `git diff` showing your changes |
+| `test-output.log` | After Step 6 (Test) | Full output from test command |
+| `analysis.md` | After Step 6 (Test) | Why it worked/failed, insights learned |
+
+**Example approach.md:**
+```markdown
+## Approach: Geometric Off-Screen Check
+
+Skip RequestApplyInsets for views completely off-screen using simple bounds check:
+`viewLeft >= screenWidth || viewRight <= 0 || viewTop >= screenHeight || viewBottom <= 0`
+
+**Different from existing fix:** Current fix uses HashSet tracking. This approach uses pure geometry with no state.
+```
+
+**Example result.txt:**
+```
+Pass
+```

-Save artifacts to `CustomAgentLogsTmp/PRState/<PRNumber>/try-fix/attempt-<N>/` with files: `approach.md`, `fix.diff`, `test-output.log`, `result.txt`, `analysis.md`.

-See [references/output-structure.md](references/output-structure.md) for setup commands and directory structure details.

 ## Completion Criteria

@@ -61,6 +121,26 @@ The skill is complete when:
 - [ ] Baseline restored (working directory clean)
 - [ ] Results reported to invoker

+🚨 **CRITICAL: What counts as "Pass" vs "Fail"**
+
+| Scenario | Result | Explanation |
+|----------|--------|-------------|
+| Test command runs, tests pass | ✅ **Pass** | Actual validation |
+| Test command runs, tests fail | ❌ **Fail** | Fix didn't work |
+| Code compiles but no device available | ⚠️ **Blocked** | Device/emulator unavailable - report with explanation |
+| Code compiles but test command errors | ❌ **Fail** | Infrastructure issue is still a failure |
+| Code doesn't compile | ❌ **Fail** | Fix is broken |
+
+**NEVER claim "Pass" based on:**
+- ❌ "Code compiles successfully" alone
+- ❌ "Code review validates the logic"
+- ❌ "The approach is sound"
+- ❌ "Device was unavailable but fix looks correct"
+
+**Pass REQUIRES:** The test command executed AND reported test success.
+
+**If device/emulator is unavailable:** Report `result.txt` = `Blocked` with explanation. Do NOT manufacture a Pass.
+
 **Exhaustion criteria:** Stop after 3 iterations if:
 1. Code compiles but tests consistently fail for same reason
 2. Root cause analysis reveals fundamental flaw in approach
@@ -110,12 +190,19 @@ The skill is complete when:

 🚨 **ALWAYS use EstablishBrokenBaseline.ps1 - NEVER manually revert files.**

-```bash
-pwsh .github/scripts/EstablishBrokenBaseline.ps1
+```powershell
+# Capture baseline output as proof it was run
+pwsh .github/scripts/EstablishBrokenBaseline.ps1 *>&1 | Tee-Object -FilePath "$OUTPUT_DIR/baseline.log"
 ```

 The script auto-detects and reverts fix files to merge-base state while preserving test files. **Will fail fast if no fix files detected** - you must be on the actual PR branch. Optional flags: `-BaseBranch main`, `-DryRun`.

+**Verify baseline was established:**
+```powershell
+# baseline.log should contain "Baseline established" and list of reverted files
+Select-String -Path "$OUTPUT_DIR/baseline.log" -Pattern "Baseline established"
+```
+
 **If the script fails with "No fix files detected":** You're likely on the wrong branch. Checkout the actual PR branch with `gh pr checkout <PR#>` and try again.

 **If something fails mid-attempt:** `pwsh .github/scripts/EstablishBrokenBaseline.ps1 -Restore`
@@ -139,6 +226,18 @@ Based on your analysis and any provided hints, design a single fix approach:

 **If hints suggest specific approaches**, prioritize those.

+**IMMEDIATELY create `approach.md`** in your output directory:
+
+```powershell
+@"
+## Approach: [Brief Name]
+
+[Description of what you're changing and why]
+
+**Different from existing fix:** [How this differs from PR's current approach]
+"@ | Set-Content "$OUTPUT_DIR/approach.md"
+```
+
 ### Step 5: Apply the Fix

 Implement your fix. Use `git status --short` and `git diff` to track changes.
@@ -153,8 +252,9 @@ Implement your fix. Use `git status --short` and `git diff` to track changes.
 - Running tests
 - Capturing logs

-```bash
-pwsh .github/scripts/BuildAndRunHostApp.ps1 -Platform <platform> -TestFilter "<filter>"
+```powershell
+# Capture output to test-output.log while also displaying it
+pwsh .github/scripts/BuildAndRunHostApp.ps1 -Platform <platform> -TestFilter "<filter>" *>&1 | Tee-Object -FilePath "$OUTPUT_DIR/test-output.log"
 ```

 **Testing Loop (Iterate until SUCCESS or exhausted):**
@@ -174,21 +274,47 @@ pwsh .github/scripts/BuildAndRunHostApp.ps1 -Platform <platform> -TestFilter "<f

 See [references/compile-errors.md](references/compile-errors.md) for error patterns and iteration examples.

-### Step 7: Capture Artifacts
+### Step 7: Capture Artifacts (MANDATORY)
+
+**Before reverting, save ALL required files to `$OUTPUT_DIR`:**
+
+```powershell
+# 1. Save result (MUST be exactly "Pass", "Fail", or "Blocked")
+"Pass" | Set-Content "$OUTPUT_DIR/result.txt"  # or "Fail"
+
+# 2. Save the diff
+git diff | Set-Content "$OUTPUT_DIR/fix.diff"
+
+# 3. Save test output (should already exist from Step 6)
+# Copy-Item "path/to/test-output.log" "$OUTPUT_DIR/test-output.log"
+
+# 4. Save analysis
+@"
+## Analysis

-Before reverting, save all artifacts to `$OUTPUT_DIR/`:
+**Result:** Pass/Fail/Blocked

-| File | Content |
-|------|---------|
-| `approach.md` | What was tried, strategy used, why different from existing fixes |
-| `fix.diff` | `git diff` output |
-| `analysis.md` | Result, hypothesis, what happened, why it worked/failed, insights for future |
+**What happened:** [Description of test results]
+
+**Why it worked/failed:** [Root cause analysis]
+
+**Insights:** [What was learned that could help future attempts]
+"@ | Set-Content "$OUTPUT_DIR/analysis.md"
+```
+
+**Verify all required files exist:**
+```powershell
+@("baseline.log", "approach.md", "result.txt", "fix.diff", "analysis.md", "test-output.log") | ForEach-Object {
+    if (Test-Path "$OUTPUT_DIR/$_") { Write-Host "✅ $_" }
+    else { Write-Host "❌ MISSING: $_" }
+}
+```

 **Analysis quality matters.** Bad: "Didn't work". Good: "Fix attempted to reset state in OnPageSelected, but this fires after layout measurement. The cached value was already used."

 ### Step 8: Restore Working Directory (MANDATORY)

-🚨 **ALWAYS restore, even if fix failed.**
+**ALWAYS restore, even if fix failed.**

 ```bash
 pwsh .github/scripts/EstablishBrokenBaseline.ps1 -Restore
diff --git a/.github/skills/try-fix/references/output-structure.md b/.github/skills/try-fix/references/output-structure.md
deleted file mode 100644
index 7e422620deb4..000000000000
--- a/.github/skills/try-fix/references/output-structure.md
+++ /dev/null
@@ -1,41 +0,0 @@
-# Output Structure Reference
-
-All try-fix artifacts are saved to: `CustomAgentLogsTmp/PRState/<PRNumber>/try-fix/attempt-<N>/`
-
-## Required Files Per Attempt
-
-| File | Description |
-|------|-------------|
-| `approach.md` | Brief description of the fix approach |
-| `fix.diff` | Git diff of the changes made |
-| `test-output.log` | Full test command output |
-| `result.txt` | PASS or FAIL |
-| `analysis.md` | Detailed analysis of why it worked/failed |
-
-## Example Structure
-
-```
-CustomAgentLogsTmp/PRState/27847/try-fix/
-├── attempt-1/
-│   ├── approach.md
-│   ├── fix.diff
-│   ├── test-output.log
-│   ├── result.txt
-│   └── analysis.md
-├── attempt-2/
-│   └── ...
-└── summary.md  # Overall summary of all attempts
-```
-
-## Setup Commands
-
-```bash
-# Auto-detect PR number
-PR_NUMBER=$(git branch --show-current | sed -n 's/^pr-\([0-9]\+\).*/\1/p')
-# Or: PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null)
-
-# Determine attempt number and create directory
-ATTEMPT_NUM=$(($(ls -d CustomAgentLogsTmp/PRState/$PR_NUMBER/try-fix/attempt-* 2>/dev/null | wc -l) + 1))
-OUTPUT_DIR="CustomAgentLogsTmp/PRState/$PR_NUMBER/try-fix/attempt-$ATTEMPT_NUM"
-mkdir -p "$OUTPUT_DIR"
-```

PATCH

echo "Patch applied successfully."
