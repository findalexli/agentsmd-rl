#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'titleSection' .github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/skills/ai-summary-comment/SKILL.md b/.github/skills/ai-summary-comment/SKILL.md
index 185e7af83af5..a5ee581267c2 100644
--- a/.github/skills/ai-summary-comment/SKILL.md
+++ b/.github/skills/ai-summary-comment/SKILL.md
@@ -56,10 +56,11 @@ Most scripts post to the **same single comment** identified by `<!-- AI Summary

 ### Separate PR Finalization Comment

-The `post-pr-finalize-comment.ps1` script posts a **separate comment** identified by `<!-- PR-FINALIZE-COMMENT -->`. This is intentional because:
-- Finalization reviews can happen multiple times (after each commit)
-- Each review is numbered (Review 1, Review 2, etc.)
-- Keeps finalization reviews distinct from automated analysis
+The `post-pr-finalize-comment.ps1` script posts a **separate comment** identified by `<!-- PR-FINALIZE-COMMENT -->`. This comment contains two sections:
+- **Title**: Shows the suggested PR title with comparison to current
+- **Description**: Shows the suggested PR description
+
+If an existing finalize comment exists, it will be replaced with the updated Title and Description sections. This keeps finalization reviews distinct from automated analysis.

 ## Section Scripts

diff --git a/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 b/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
index f1aaade8f45d..0cfcf8928bb2 100644
--- a/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
+++ b/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
@@ -4,12 +4,12 @@
     Posts or updates a PR finalize comment on a GitHub Pull Request.

 .DESCRIPTION
-    Creates ONE comment for PR finalization reviews with each review in a collapsible section.
+    Creates ONE comment for PR finalization with two collapsible sections: Title and Description.
     Uses HTML marker <!-- PR-FINALIZE-COMMENT --> for identification.

-    **NEW: Auto-loads from CustomAgentLogsTmp/PRState/{PRNumber}/pr-finalize/**
+    **Auto-loads from CustomAgentLogsTmp/PRState/{PRNumber}/pr-finalize/**

-    If an existing finalize comment exists, it will be EDITED with the new review added.
+    If an existing finalize comment exists, it will be REPLACED with the new content.
     Otherwise, a new comment will be created.

     Format:
@@ -17,15 +17,13 @@
     <!-- PR-FINALIZE-COMMENT -->

     <details>
-    <summary><b>Review 1: Title and description check ✅ Ready</b></summary>
-
-    ... review details ...
+    <summary><b>Title: ✅ Good</b></summary>
+    ... title details ...
     </details>

     <details>
-    <summary><b>Review 2: Updated after implementation change ⚠️ Needs Update</b></summary>
-
-    ... review details ...
+    <summary><b>Description: ⚠️ Needs Update</b></summary>
+    ... description details ...
     </details>

 .PARAMETER PRNumber
@@ -34,12 +32,6 @@
 .PARAMETER SummaryFile
     Path to pr-finalize-summary.md file. If provided, auto-loads review data from this file.

-.PARAMETER ReviewNumber
-    The review number (1, 2, 3, etc.) - auto-detected from SummaryFile if not specified
-
-.PARAMETER ReviewDescription
-    Brief description of what was reviewed (required unless loading from SummaryFile)
-
 .PARAMETER TitleStatus
     Title assessment: "Good", "NeedsUpdate" (required unless loading from SummaryFile)

@@ -49,6 +41,9 @@
 .PARAMETER RecommendedTitle
     Recommended PR title (optional - only if TitleStatus is NeedsUpdate)

+.PARAMETER TitleIssues
+    List of issues with the current title (optional - only if TitleStatus is NeedsUpdate)
+
 .PARAMETER DescriptionStatus
     Description assessment: "Excellent", "Good", "NeedsUpdate", "NeedsRewrite" (required unless loading from SummaryFile)

@@ -73,9 +68,8 @@
     ./post-pr-finalize-comment.ps1 -SummaryFile CustomAgentLogsTmp/PRState/27246/pr-finalize/pr-finalize-summary.md

 .EXAMPLE
-    # Manual parameters (legacy)
-    ./post-pr-finalize-comment.ps1 -PRNumber 25748 -ReviewNumber 1 `
-        -ReviewDescription "Initial finalization check" `
+    # Manual parameters
+    ./post-pr-finalize-comment.ps1 -PRNumber 25748 `
         -TitleStatus "Good" `
         -CurrentTitle "[iOS] Fix SafeArea padding calculation" `
         -DescriptionStatus "Good" `
@@ -89,12 +83,6 @@ param(
     [Parameter(Mandatory=$false)]
     [string]$SummaryFile,

-    [Parameter(Mandatory=$false)]
-    [int]$ReviewNumber,
-
-    [Parameter(Mandatory=$false)]
-    [string]$ReviewDescription,
-
     [Parameter(Mandatory=$false)]
     [ValidateSet("Good", "NeedsUpdate", "")]
     [string]$TitleStatus,
@@ -105,6 +93,9 @@ param(
     [Parameter(Mandatory=$false)]
     [string]$RecommendedTitle,

+    [Parameter(Mandatory=$false)]
+    [string]$TitleIssues,
+
     [Parameter(Mandatory=$false)]
     [ValidateSet("Excellent", "Good", "NeedsUpdate", "NeedsRewrite", "")]
     [string]$DescriptionStatus,
@@ -166,38 +157,20 @@ if (-not [string]::IsNullOrWhiteSpace($SummaryFile)) {
         Write-Host "ℹ️  Auto-detected PRNumber: $PRNumber from path" -ForegroundColor Cyan
     }

-    # Extract ReviewNumber (default to 1)
-    if ($ReviewNumber -eq 0) {
-        # Check if there's a review number in the content
-        if ($content -match 'Review (\d+)') {
-            $ReviewNumber = [int]$Matches[1]
-        } else {
-            $ReviewNumber = 1
-        }
-        Write-Host "ℹ️  Using ReviewNumber: $ReviewNumber" -ForegroundColor Cyan
-    }
-
-    # Extract verdict for ReviewDescription
-    if ([string]::IsNullOrWhiteSpace($ReviewDescription)) {
-        if ($content -match '✅\s*No Changes Needed') {
-            $ReviewDescription = "Finalization check - Ready"
-        } elseif ($content -match '⚠️\s*Needs Updates') {
-            $ReviewDescription = "Finalization check - Needs Updates"
-        } else {
-            $ReviewDescription = "Finalization review"
-        }
-    }
-
     # Extract Title assessment
     if ([string]::IsNullOrWhiteSpace($TitleStatus)) {
-        # Check if there are title issues or a recommended title
-        $hasRecommendedTitle = $content -match '\*\*Recommended.*?Title'
-        $hasTitleIssues = $content -match '(?s)### 📋 Title Assessment.+?\*\*Issues:\*\*'
-
-        if ($hasRecommendedTitle -or $hasTitleIssues) {
+        # Look for explicit status in Title Assessment section
+        if ($content -match '(?s)### 📋 Title Assessment.+?\*\*Status:\*\*\s*(✅|❌|⚠️)?\s*(Good|NeedsUpdate|Needs Update)') {
+            $statusMatch = $Matches[2] -replace '\s+', ''
+            if ($statusMatch -eq "Good") {
+                $TitleStatus = "Good"
+            } else {
+                $TitleStatus = "NeedsUpdate"
+            }
+        }
+        # Fallback: check for recommended title specifically in title section
+        elseif ($content -match '(?s)### 📋 Title Assessment.+?\*\*Recommended.*?Title') {
             $TitleStatus = "NeedsUpdate"
-        } elseif ($content -match '### Title.*?✅') {
-            $TitleStatus = "Good"
         } else {
             $TitleStatus = "Good"
         }
@@ -342,14 +315,6 @@ if ($PRNumber -eq 0) {
     throw "PRNumber is required. Provide via -PRNumber or use -SummaryFile with path containing PR number"
 }

-if ($ReviewNumber -eq 0) {
-    $ReviewNumber = 1
-}
-
-if ([string]::IsNullOrWhiteSpace($ReviewDescription)) {
-    throw "ReviewDescription is required. Provide via -ReviewDescription or use -SummaryFile"
-}
-
 if ([string]::IsNullOrWhiteSpace($TitleStatus)) {
     $TitleStatus = "Good"
 }
@@ -373,6 +338,17 @@ if ([string]::IsNullOrWhiteSpace($DescriptionAssessment)) {
     throw "DescriptionAssessment is required. Provide via -DescriptionAssessment or use -SummaryFile"
 }

+# Initialize $titleIssues from parameter if provided, otherwise set default based on status
+if (-not (Get-Variable -Name 'titleIssues' -ErrorAction SilentlyContinue) -or [string]::IsNullOrWhiteSpace($titleIssues)) {
+    if (-not [string]::IsNullOrWhiteSpace($TitleIssues)) {
+        $titleIssues = $TitleIssues
+    } elseif ($TitleStatus -eq "Good") {
+        $titleIssues = "Title is clear and follows conventions."
+    } else {
+        $titleIssues = ""
+    }
+}
+
 # Status emoji mapping
 $titleEmoji = switch ($TitleStatus) {
     "Good" { "✅" }
@@ -388,15 +364,6 @@ $descEmoji = switch ($DescriptionStatus) {
     default { "" }
 }

-# Overall status
-$overallStatus = if ($TitleStatus -eq "Good" -and ($DescriptionStatus -eq "Excellent" -or $DescriptionStatus -eq "Good")) {
-    "✅ Ready"
-} elseif ($DescriptionStatus -eq "NeedsRewrite") {
-    "❌ Needs Rewrite"
-} else {
-    "⚠️ Needs Update"
-}
-
 # Format status with spaces for display
 $titleStatusDisplay = switch ($TitleStatus) {
     "NeedsUpdate" { "Needs Update" }
@@ -409,45 +376,47 @@ $descStatusDisplay = switch ($DescriptionStatus) {
     default { $DescriptionStatus }
 }

-# Build the new review section (collapsible)
-$reviewSection = @"
+# Build Title section (collapsible)
+$titleSection = @"
 <details>
-<summary><b>Review $ReviewNumber`: $ReviewDescription $overallStatus</b></summary>
+<summary><b>Title: $titleEmoji $titleStatusDisplay</b></summary>

-### Title $titleEmoji $titleStatusDisplay
+<br>

 **Current:** ``$CurrentTitle``
 "@

 if (-not [string]::IsNullOrWhiteSpace($titleIssues) -and $TitleStatus -eq "NeedsUpdate") {
-    $reviewSection += "`n`n**Issues:**`n$titleIssues"
+    $titleSection += "`n`n**Issues:**`n$titleIssues"
 }

-if (-not [string]::IsNullOrWhiteSpace($RecommendedTitle)) {
-    $reviewSection += @"
+if (-not [string]::IsNullOrWhiteSpace($RecommendedTitle) -and $TitleStatus -eq "NeedsUpdate") {
+    $titleSection += @"

-<details>
-<summary>Click to see proposed title</summary>

-``$RecommendedTitle``
-
-</details>
+**Recommended:** ``$RecommendedTitle``
 "@
 }

-$reviewSection += @"
+$titleSection += @"

-<hr>
+</details>
+"@

-### Description $descEmoji $descStatusDisplay
+# Build Description section (collapsible)
+$descSection = @"
+<details>
+<summary><b>Description: $descEmoji $descStatusDisplay</b></summary>
+
+<br>

 $DescriptionAssessment

 "@

 if (-not [string]::IsNullOrWhiteSpace($MissingElements)) {
-    $reviewSection += @"
-### Missing Elements
+    $descSection += @"
+**Missing Elements:**

 $MissingElements

@@ -455,23 +424,15 @@ $MissingElements
 }

 if (-not [string]::IsNullOrWhiteSpace($RecommendedDescription)) {
-    # Format recommended description - don't wrap in code fence since content has code blocks
-    # Instead, put in a details section with clear copy instructions
-    $reviewSection += @"
-
+    $descSection += @"
 ### ✨ Suggested PR Description

-<details>
-<summary>Click to see proposed description</summary>
-
 $RecommendedDescription

-</details>
-
 "@
 }

-$reviewSection += @"
+$descSection += @"
 </details>
 "@

@@ -486,7 +447,7 @@ Write-Host "`nChecking for existing PR Finalization comment on #$PRNumber..." -F
 $existingComment = $null

 try {
-    $commentsJson = gh api "repos/dotnet/maui/issues/$PRNumber/comments" 2>$null
+    $commentsJson = gh api "repos/dotnet/maui/issues/$PRNumber/comments?per_page=100" 2>$null
     $comments = $commentsJson | ConvertFrom-Json

     foreach ($comment in $comments) {
@@ -504,34 +465,15 @@ try {
     Write-Host "✓ No existing PR Finalization comment found - will create new" -ForegroundColor Yellow
 }

-# Build the full comment body
+# Build the full comment body (always replaces existing comment entirely)
 $commentBody = @"
 ## 📋 PR Finalization Review
 $FINALIZE_MARKER

-"@
-
-if ($existingComment) {
-    # Parse existing reviews
-    $existingReviews = @()
-    $pattern = '(?s)<details>\s*<summary><b>Review (\d+):.+?</details>'
-    $matches = [regex]::Matches($existingComment.body, $pattern)
-
-    foreach ($match in $matches) {
-        $reviewNum = [int]$match.Groups[1].Value
-        if ($reviewNum -ne $ReviewNumber) {
-            $existingReviews += $match.Value
-        }
-    }
-
-    # Add existing reviews first, then new review
-    if ($existingReviews.Count -gt 0) {
-        $commentBody += ($existingReviews -join "`n`n")
-        $commentBody += "`n`n"
-    }
-}
+$titleSection

-$commentBody += $reviewSection
+$descSection
+"@

 if ($DryRun) {
     # File-based DryRun: uses separate preview file for finalize (separate comment from unified)

PATCH

echo "Patch applied successfully."
