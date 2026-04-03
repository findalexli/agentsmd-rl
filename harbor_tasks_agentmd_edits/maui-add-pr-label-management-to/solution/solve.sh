#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'Update-VerificationLabels' .github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/skills/verify-tests-fail-without-fix/SKILL.md b/.github/skills/verify-tests-fail-without-fix/SKILL.md
index c20b848c406b..ba3df1d1aaa6 100644
--- a/.github/skills/verify-tests-fail-without-fix/SKILL.md
+++ b/.github/skills/verify-tests-fail-without-fix/SKILL.md
@@ -81,7 +81,8 @@ The script auto-detects which mode to use based on whether fix files are present
 1. Fetches base branch from origin (if available)
 2. Auto-detects test classes from changed test files
 3. Runs tests (should FAIL to prove they catch the bug)
-4. Reports result
+4. **Updates PR labels** based on result
+5. Reports result

 **Full Verification Mode (fix files detected):**
 1. Fetches base branch from origin to ensure accurate diff
@@ -94,7 +95,23 @@ The script auto-detects which mode to use based on whether fix files are present
 8. **Generates markdown reports**:
    - `CustomAgentLogsTmp/TestValidation/verification-report.md` - Full detailed report
    - `CustomAgentLogsTmp/PRState/verification-report.md` - Gate section for PR agent
-9. Reports result
+9. **Updates PR labels** based on result
+10. Reports result
+
+## PR Labels
+
+The skill automatically manages two labels on the PR to indicate verification status:
+
+| Label | Color | When Applied |
+|-------|-------|--------------|
+| `s/ai-reproduction-confirmed` | 🟢 Green (#2E7D32) | Tests correctly FAIL without fix (AI verified tests catch the bug) |
+| `s/ai-reproduction-failed` | 🟠 Orange (#E65100) | Tests PASS without fix (AI verified tests don't catch the bug) |
+
+**Behavior:**
+- When verification passes, adds `s/ai-reproduction-confirmed` and removes `s/ai-reproduction-failed` if present
+- When verification fails, adds `s/ai-reproduction-failed` and removes `s/ai-reproduction-confirmed` if present
+- If a PR is re-verified after fixing tests, labels are updated accordingly
+- No label = AI hasn't verified tests yet

 ## Output Files

diff --git a/.github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1 b/.github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1
index c1e8dce9f0a7..f292c83f84fb 100644
--- a/.github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1
+++ b/.github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1
@@ -98,14 +98,34 @@ if (-not $PRNumber) {
         $PRNumber = $matches[1]
         Write-Host "✅ Auto-detected PR #$PRNumber from branch name" -ForegroundColor Green
     } else {
-        # Try gh cli
+        $foundPR = $false
+        # Try gh cli - first try 'gh pr view' for current branch
         try {
             $prInfo = gh pr view --json number 2>$null | ConvertFrom-Json
-            if ($prInfo.number) {
+            if ($prInfo -and $prInfo.number) {
                 $PRNumber = $prInfo.number
-                Write-Host "✅ Auto-detected PR #$PRNumber from gh cli" -ForegroundColor Green
+                $foundPR = $true
+                Write-Host "✅ Auto-detected PR #$PRNumber from gh cli (pr view)" -ForegroundColor Green
             }
         } catch {
+            # gh pr view failed, will try fallback
+        }
+
+        # Fallback: search for PRs with this branch as head (works across forks)
+        if (-not $foundPR) {
+            try {
+                $prList = gh pr list --head $currentBranch --json number --limit 1 2>$null | ConvertFrom-Json
+                if ($prList -and $prList.Count -gt 0 -and $prList[0].number) {
+                    $PRNumber = $prList[0].number
+                    $foundPR = $true
+                    Write-Host "✅ Auto-detected PR #$PRNumber from gh cli (pr list --head)" -ForegroundColor Green
+                }
+            } catch {
+                # gh pr list also failed
+            }
+        }
+
+        if (-not $foundPR) {
             Write-Host "⚠️  Could not auto-detect PR number - using 'unknown' folder" -ForegroundColor Yellow
             $PRNumber = "unknown"
         }
@@ -124,6 +144,60 @@ $BaselineScript = Join-Path $RepoRoot ".github/scripts/EstablishBrokenBaseline.p
 # Import Test-IsTestFile and Find-MergeBase from shared script
 . $BaselineScript

+# ============================================================
+# Label management for verification results
+# ============================================================
+$LabelConfirmed = "s/ai-reproduction-confirmed"
+$LabelFailed = "s/ai-reproduction-failed"
+
+function Update-VerificationLabels {
+    param(
+        [Parameter(Mandatory = $true)]
+        [bool]$ReproductionConfirmed,
+
+        [Parameter(Mandatory = $false)]
+        [string]$PR = $PRNumber
+    )
+
+    if ($PR -eq "unknown" -or -not $PR) {
+        Write-Host "⚠️  Cannot update labels: PR number not available" -ForegroundColor Yellow
+        return
+    }
+
+    $labelToAdd = if ($ReproductionConfirmed) { $LabelConfirmed } else { $LabelFailed }
+    $labelToRemove = if ($ReproductionConfirmed) { $LabelFailed } else { $LabelConfirmed }
+
+    Write-Host ""
+    Write-Host "🏷️  Updating verification labels on PR #$PR..." -ForegroundColor Cyan
+
+    # Track success for both operations
+    $removeSuccess = $true
+
+    # Remove the opposite label if it exists (using REST API to avoid GraphQL deprecation issues)
+    $existingLabels = gh pr view $PR --json labels --jq '.labels[].name' 2>$null
+    if ($existingLabels -contains $labelToRemove) {
+        Write-Host "   Removing: $labelToRemove" -ForegroundColor Yellow
+        gh api "repos/dotnet/maui/issues/$PR/labels/$labelToRemove" --method DELETE 2>$null | Out-Null
+        if ($LASTEXITCODE -ne 0) {
+            $removeSuccess = $false
+            Write-Host "   ⚠️  Failed to remove label: $labelToRemove" -ForegroundColor Yellow
+        }
+    }
+
+    # Add the appropriate label (using REST API to avoid GraphQL deprecation issues)
+    Write-Host "   Adding: $labelToAdd" -ForegroundColor Green
+    $result = gh api "repos/dotnet/maui/issues/$PR/labels" --method POST -f "labels[]=$labelToAdd" 2>&1
+    $addSuccess = $LASTEXITCODE -eq 0
+
+    if ($addSuccess -and $removeSuccess) {
+        Write-Host "✅ Labels updated successfully" -ForegroundColor Green
+    } elseif ($addSuccess) {
+        Write-Host "⚠️  Label added but failed to remove old label" -ForegroundColor Yellow
+    } else {
+        Write-Host "⚠️  Failed to update labels: $result" -ForegroundColor Yellow
+    }
+}
+
 # ============================================================
 # Auto-detect test filter from changed files
 # ============================================================
@@ -392,6 +466,7 @@ if ($DetectedFixFiles.Count -eq 0) {
         Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
         Write-Host ""
         Write-Host "Failed tests: $($testResult.FailCount)" -ForegroundColor Yellow
+        Update-VerificationLabels -ReproductionConfirmed $true
         exit 0
     } else {
         # Tests PASSED - this is bad!
@@ -412,6 +487,7 @@ if ($DetectedFixFiles.Count -eq 0) {
         Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Red
         Write-Host ""
         Write-Host "Passed tests: $($testResult.PassCount)" -ForegroundColor Yellow
+        Update-VerificationLabels -ReproductionConfirmed $false
         exit 1
     }
 }
@@ -710,9 +786,10 @@ Write-Log "=========================================="

 foreach ($file in $RevertableFiles) {
     Write-Log "  Reverting: $file"
-    git checkout $MergeBase -- $file 2>&1 | Out-Null
+    $gitOutput = git checkout $MergeBase -- $file 2>&1
     if ($LASTEXITCODE -ne 0) {
         Write-Log "  ERROR: Failed to revert $file from $MergeBase"
+        Write-Log "  Git output: $gitOutput"
         exit 1
     }
 }
@@ -739,9 +816,10 @@ Write-Log "=========================================="

 foreach ($file in $RevertableFiles) {
     Write-Log "  Restoring: $file"
-    git checkout HEAD -- $file 2>&1 | Out-Null
+    $gitOutput = git checkout HEAD -- $file 2>&1
     if ($LASTEXITCODE -ne 0) {
         Write-Log "  ERROR: Failed to restore $file from HEAD"
+        Write-Log "  Git output: $gitOutput"
         exit 1
     }
 }
@@ -806,6 +884,7 @@ if ($verificationPassed) {
     Write-Host "║  - FAIL without fix (as expected)                         ║" -ForegroundColor Green
     Write-Host "║  - PASS with fix (as expected)                            ║" -ForegroundColor Green
     Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
+    Update-VerificationLabels -ReproductionConfirmed $true
     exit 0
 } else {
     Write-Host ""
@@ -827,5 +906,6 @@ if ($verificationPassed) {
     Write-Host "║  3. The issue was already fixed in base branch            ║" -ForegroundColor Red
     Write-Host "║  4. Build caching - try clean rebuild                     ║" -ForegroundColor Red
     Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Red
+    Update-VerificationLabels -ReproductionConfirmed $false
     exit 1
 }

PATCH

echo "Patch applied successfully."
