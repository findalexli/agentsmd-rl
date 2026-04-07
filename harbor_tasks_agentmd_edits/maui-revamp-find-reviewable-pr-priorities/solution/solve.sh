#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'Get-ReadyToReviewPRNumbers' .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply full gold patch (both script and SKILL.md changes)
git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/skills/find-reviewable-pr/SKILL.md b/.github/skills/find-reviewable-pr/SKILL.md
index 2b7f5fcf23a7..2a5edae6fe63 100644
--- a/.github/skills/find-reviewable-pr/SKILL.md
+++ b/.github/skills/find-reviewable-pr/SKILL.md
@@ -22,25 +22,40 @@ This skill searches the dotnet/maui and dotnet/docs-maui repositories for open p

 ## Priority Categories (in order)

-1. **Priority (P/0)** - Critical priority PRs that need immediate attention
-2. **Milestoned** - PRs assigned to current milestone(s), sorted by lowest SR number first (e.g., SR5 before SR6), then Servicing
-3. **Partner** - PRs from Syncfusion and other partners
-4. **Community** - External contributions needing review
-5. **Recent Waiting for Review** - PRs created in last 2 weeks that need review (minimum 5)
-6. **docs-maui Waiting for Review** - Documentation PRs needing review (minimum 5)
+1. **Priority (P/0)** - Critical priority PRs that need immediate attention (always on top)
+2. **Approved (Not Merged)** - PRs with human approval that haven't been merged yet
+3. **Ready To Review (Project Board)** - PRs in "Ready To Review" column of the MAUI SDK Ongoing project board (requires `read:project` scope)
+4. **Milestoned** - PRs assigned to current milestone(s), sorted by lowest SR number first (e.g., SR5 before SR6), then Servicing
+5. **Agent Reviewed** - PRs reviewed by AI agent workflow (detected via labels)
+6. **Partner** - PRs from Syncfusion and other partners
+7. **Community** - External contributions needing review
+8. **Recent Waiting for Review** - PRs created in last 2 weeks that need review (minimum 5)
+9. **docs-maui Waiting for Review** - Documentation PRs needing review (minimum 5)

 ## Quick Start

 ```bash
-# Find all reviewable PRs (shows top from each category including docs-maui)
+# Find P/0 and milestoned PRs (default behavior, excludes changes-requested)
 pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1

+# Find all reviewable PRs across all categories
+pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category all
+
 # Find only milestoned PRs
 pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category milestoned

 # Find only docs-maui PRs waiting for review
 pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category docs-maui

+# Find approved PRs waiting to be merged
+pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category approved
+
+# Find PRs in "Ready To Review" on the project board
+pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category ready-to-review
+
+# Find agent-reviewed PRs with merge summaries
+pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category agent-reviewed
+
 # Find recent PRs waiting for review
 pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Category recent

@@ -58,9 +73,9 @@ pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -DocsLim

 | Parameter | Values | Default | Description |
 |-----------|--------|---------|-------------|
-| `-Category` | milestoned, priority, recent, partner, community, docs-maui, all | all | Filter by category |
+| `-Category` | default, milestoned, priority, recent, partner, community, docs-maui, approved, ready-to-review, agent-reviewed, all | default | Filter by category. `default` shows only P/0 + milestoned, excluding changes-requested PRs. |
 | `-Platform` | android, ios, windows, maccatalyst, all | all | Filter by platform |
-| `-Limit` | 1-100 | 10 | Max PRs per category (maui repo) |
+| `-Limit` | 1-100 | 100 | Max PRs per category (maui repo) |
 | `-RecentLimit` | 1-100 | 5 | Max recent PRs waiting for review from maui repo (minimum 5 enforced) |
 | `-DocsLimit` | 1-100 | 5 | Max PRs for docs-maui waiting for review (minimum 5 enforced) |
 | `-ExcludeAuthors` | string[] | (none) | Exclude PRs from specific authors (e.g., `-ExcludeAuthors PureWeen,rmarinho`) |
@@ -71,10 +86,10 @@ pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -DocsLim

 ### Step 1: Find PRs to Review

-**CRITICAL**: You MUST use the PowerShell script below. Do NOT attempt to query GitHub directly with `gh` commands or `jq` if the script fails. The script contains important prioritization logic (SR3 before SR4, P/0 first, etc.) that cannot be replicated with ad-hoc queries.
+**CRITICAL**: You MUST use the PowerShell script below. Do NOT attempt to query GitHub directly with `gh` commands or `jq` if the script fails. The script contains important prioritization logic (SR5 before SR6, P/0 first, etc.) that cannot be replicated with ad-hoc queries.

 ```bash
-pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 -Limit 5
+pwsh .github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1
 ```

 **If the script fails** (e.g., HTTP 502, network error, authentication issue):
@@ -97,44 +112,17 @@ To enable: `gh auth refresh -s read:project`

 **CRITICAL**: When presenting PR results, you MUST include PRs from ALL categories returned by the script:

-1. 🔴 **Priority (P/0)** - Always include if present
-2. 📅 **Milestoned** - Always include if present
-3. 🤝 **Partner** - Always include if present
-4. ✨ **Community** - Always include if present
-5. 🕐 **Recent** - Always include if present
-6. 📖 **docs-maui** - Always include if present
-
-**DO NOT** omit any category. Each category table should include columns for: PR, Title, Author, Platform/Repo, Status, Age, Updated.
-
-### Step 4: Present ONE PR at a Time for Review
-
-When user asks to review, present only ONE PR in this format:
-
-```markdown
-## PR #XXXXX
-
-**[Title]**
-
-🔗 [URL]
-
-| Field | Value |
-|-------|-------|
-| **Author** | username |
-| **Platform** | platform |
-| **Complexity** | Easy/Medium/Complex |
-| **Milestone** | milestone or (none) |
-| **Age** | X days |
-| **Files** | X (+additions/-deletions) |
-| **Labels** | labels |
-| **Category** | priority/milestoned/partner/community/recent |
-
-Would you like me to review this PR?
-```
-
-### Step 5: Invoke PR Reviewer
+1. 🔴 **Priority (P/0)** - Always include if present (always first)
+2. 🟢 **Approved (Not Merged)** - Always include if present
+3. 📋 **Ready To Review (Board)** - Always include if present
+4. 📅 **Milestoned** - Always include if present
+5. 🤖 **Agent Reviewed** - Always include if present
+6. 🤝 **Partner** - Always include if present
+7. ✨ **Community** - Always include if present
+8. 🕐 **Recent** - Always include if present
+9. 📖 **docs-maui** - Always include if present

-When user confirms, use the **pr** agent:
-- "Review PR #XXXXX"
+**DO NOT** omit any category. Each category table should include columns for: PR, Title, Author, Assignees, Platform/Repo, Status, Agent Review, Age, Updated.

 ## Complexity Levels

@@ -146,7 +134,10 @@ When user confirms, use the **pr** agent:

 ## Tips

-- **P/0 PRs** should be reviewed first - they're blocking releases
+- **P/0 PRs** should always be reviewed first - they're blocking releases
+- **Approved PRs** are ready to merge - verify CI is green and merge
+- **Ready To Review PRs** are in the project board pipeline and need timely review
+- **Agent Reviewed PRs** have been analyzed by the AI agent workflow - check their labels for status
 - **Milestoned PRs** have deadlines and should be prioritized
 - **Partner PRs** often have business priority
 - **Community PRs** may need more guidance and thorough review
diff --git a/.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1 b/.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1
index 50e0316b6492..439d03b5bf0d 100644
--- a/.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1
+++ b/.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1
@@ -5,21 +5,24 @@

 .DESCRIPTION
     This script queries GitHub for open PRs and prioritizes them by:
-    1. Milestoned PRs (dynamically sorted by SR number - lower numbers first, e.g., SR5 before SR6)
-    2. P/0 labeled PRs (critical priority)
-    3. Recent PRs (5 from maui + 5 from docs-maui by default)
-    4. Partner PRs (Syncfusion, etc.)
-    5. Community PRs (external contributions)
-    6. docs-maui PRs (5 priority + 5 recent by default)
+    1. P/0 labeled PRs (critical priority - always on top)
+    2. Approved (not merged) PRs
+    3. Ready To Review (from project board)
+    4. Milestoned PRs (dynamically sorted by SR number - lower numbers first, e.g., SR5 before SR6)
+    5. Agent Reviewed PRs (detected via labels)
+    6. Partner PRs (Syncfusion, etc.)
+    7. Community PRs (external contributions)
+    8. Recent PRs waiting for review (last 2 weeks)
+    9. docs-maui PRs (priority + waiting for review)

 .PARAMETER Category
-    Filter by category: "milestoned", "priority", "recent", "partner", "community", "docs-maui", "all"
+    Filter by category: "default" (P/0 + milestoned only), "milestoned", "priority", "recent", "partner", "community", "docs-maui", "approved", "ready-to-review", "agent-reviewed", "all"

 .PARAMETER Platform
     Filter by platform: "android", "ios", "windows", "maccatalyst", "all"

 .PARAMETER Limit
-    Maximum number of PRs to return per category (default: 10)
+    Maximum number of PRs to return per category (default: 100)

 .PARAMETER RecentLimit
     Maximum number of recent PRs to return from maui (default: 5)
@@ -32,7 +35,11 @@

 .EXAMPLE
     ./query-reviewable-prs.ps1
-    # Returns prioritized PRs across all categories including 5 recent from maui and 5 from docs-maui
+    # Returns only P/0 and Milestoned PRs (default behavior)
+
+.EXAMPLE
+    ./query-reviewable-prs.ps1 -Category all
+    # Returns PRs across all categories

 .EXAMPLE
     ./query-reviewable-prs.ps1 -Category milestoned -Platform android
@@ -45,15 +52,15 @@

 param(
     [Parameter(Mandatory = $false)]
-    [ValidateSet("milestoned", "priority", "recent", "partner", "community", "docs-maui", "all")]
-    [string]$Category = "all",
+    [ValidateSet("default", "milestoned", "priority", "recent", "partner", "community", "docs-maui", "approved", "ready-to-review", "agent-reviewed", "all")]
+    [string]$Category = "default",

     [Parameter(Mandatory = $false)]
     [ValidateSet("android", "ios", "windows", "maccatalyst", "all")]
     [string]$Platform = "all",

     [Parameter(Mandatory = $false)]
-    [int]$Limit = 10,
+    [int]$Limit = 100,

     [Parameter(Mandatory = $false)]
     [int]$RecentLimit = 5,
@@ -138,6 +145,81 @@ function Invoke-GitHubWithRetry {
     throw "Failed to $Description after $MaxRetries attempts"
 }

+# MAUI SDK Ongoing project board constants
+$MAUI_PROJECT_ID = "PVT_kwDOAIt-yc4AH1zp"
+$READY_TO_REVIEW_OPTION_ID = "11d42e2a"
+
+# Helper function to fetch PR numbers in "Ready To Review" from the project board
+function Get-ReadyToReviewPRNumbers {
+    param([bool]$HasProjectScope)
+
+    if (-not $HasProjectScope) {
+        Write-Host "  ⚠ Skipping project board query (missing read:project scope)" -ForegroundColor Yellow
+        return @()
+    }
+
+    Write-Host "  Fetching 'Ready To Review' items from MAUI SDK Ongoing board..." -ForegroundColor Gray
+
+    try {
+        $readyPRs = @()
+        $hasNextPage = $true
+        $endCursor = $null
+
+        while ($hasNextPage) {
+            $afterClause = if ($endCursor) { ", after: `"$endCursor`"" } else { "" }
+            $graphqlQuery = @"
+{
+  node(id: "$MAUI_PROJECT_ID") {
+    ... on ProjectV2 {
+      items(first: 100$afterClause) {
+        pageInfo {
+          hasNextPage
+          endCursor
+        }
+        nodes {
+          fieldValueByName(name: "Status") {
+            ... on ProjectV2ItemFieldSingleSelectValue {
+              optionId
+            }
+          }
+          content {
+            ... on PullRequest {
+              number
+              state
+            }
+          }
+        }
+      }
+    }
+  }
+}
+"@
+            $result = Invoke-GitHubWithRetry -Command "gh api graphql -f query='$($graphqlQuery -replace "`r?`n", " " -replace "'", "'\''")'" -Description "fetch project board items"
+            $parsed = $result | ConvertFrom-Json
+
+            foreach ($item in $parsed.data.node.items.nodes) {
+                if ($item.fieldValueByName -and
+                    $item.fieldValueByName.optionId -eq $READY_TO_REVIEW_OPTION_ID -and
+                    $item.content -and
+                    $item.content.number -and
+                    $item.content.state -eq "OPEN") {
+                    $readyPRs += $item.content.number
+                }
+            }
+
+            $hasNextPage = $parsed.data.node.items.pageInfo.hasNextPage
+            $endCursor = $parsed.data.node.items.pageInfo.endCursor
+        }
+
+        Write-Host "    Ready To Review: $($readyPRs.Count) PRs" -ForegroundColor Gray
+        return $readyPRs
+    }
+    catch {
+        Write-Warning "  Could not query project board: $_"
+        return @()
+    }
+}
+
 # Check if we have read:project scope by testing a simple query with projectItems
 $hasProjectScope = $true
 Write-Host ""
@@ -163,9 +245,12 @@ catch {
 }

 # Build the JSON fields list based on available scopes
-$baseFields = "number,title,labels,createdAt,updatedAt,isDraft,author,additions,deletions,changedFiles,milestone,url,reviewDecision,reviews"
+$baseFields = "number,title,labels,createdAt,updatedAt,isDraft,author,assignees,additions,deletions,changedFiles,milestone,url,reviewDecision,reviews"
 $jsonFields = if ($hasProjectScope) { "$baseFields,projectItems" } else { $baseFields }

+# Fetch "Ready To Review" PR numbers from the project board
+$readyToReviewPRNumbers = Get-ReadyToReviewPRNumbers -HasProjectScope $hasProjectScope
+
 # Fetch PRs from dotnet/maui using multiple targeted queries to ensure comprehensive coverage
 Write-Host ""
 Write-Host "Fetching open PRs from dotnet/maui..." -ForegroundColor Cyan
@@ -247,6 +332,27 @@ try {
     $added = Add-UniquePRs -prs $prs -allPRs ([ref]$allPRs) -seenNumbers ([ref]$seenPRNumbers)
     Write-Host "    Recently created: $added PRs" -ForegroundColor Gray

+    # Query 7: Approved but not merged PRs
+    Write-Host "  Fetching approved (not merged) PRs..." -ForegroundColor Gray
+    $prResult = Invoke-GitHubWithRetry -Command "gh pr list --repo dotnet/maui --state open --search 'review:approved' --limit 25 --json $jsonFields" -Description "fetch approved PRs"
+    $prs = $prResult | ConvertFrom-Json
+    $added = Add-UniquePRs -prs $prs -allPRs ([ref]$allPRs) -seenNumbers ([ref]$seenPRNumbers)
+    Write-Host "    Approved (not merged): $added PRs" -ForegroundColor Gray
+
+    # Query 8: Agent-reviewed PRs
+    Write-Host "  Fetching agent-reviewed PRs..." -ForegroundColor Gray
+    $prResult = Invoke-GitHubWithRetry -Command "gh pr list --repo dotnet/maui --state open --search 'label:s/agent-reviewed' --limit 25 --json $jsonFields" -Description "fetch agent-reviewed PRs"
+    $prs = $prResult | ConvertFrom-Json
+    $added = Add-UniquePRs -prs $prs -allPRs ([ref]$allPRs) -seenNumbers ([ref]$seenPRNumbers)
+    Write-Host "    Agent-reviewed: $added PRs" -ForegroundColor Gray
+
+    # Query 9: Agent-approved PRs
+    Write-Host "  Fetching agent-approved PRs..." -ForegroundColor Gray
+    $prResult = Invoke-GitHubWithRetry -Command "gh pr list --repo dotnet/maui --state open --search 'label:s/agent-approved' --limit 25 --json $jsonFields" -Description "fetch agent-approved PRs"
+    $prs = $prResult | ConvertFrom-Json
+    $added = Add-UniquePRs -prs $prs -allPRs ([ref]$allPRs) -seenNumbers ([ref]$seenPRNumbers)
+    Write-Host "    Agent-approved: $added PRs" -ForegroundColor Gray
+
     # Filter out drafts
     $allPRs = $allPRs | Where-Object { -not $_.isDraft }

@@ -470,10 +576,28 @@ foreach ($pr in $allPRs) {
     $categories = Get-PRCategory -pr $pr
     $labelNames = ($pr.labels | ForEach-Object { $_.name }) -join ", "

+    # Detect agent labels
+    $labelList = $pr.labels | ForEach-Object { $_.name }
+    $isAgentApproved = $labelList -contains "s/agent-approved"
+    $isAgentReviewed = $labelList -contains "s/agent-reviewed"
+    $isAgentChangesRequested = $labelList -contains "s/agent-changes-requested"
+    $hasAgentReview = $isAgentApproved -or $isAgentReviewed -or $isAgentChangesRequested
+    $agentStatus = if ($isAgentApproved) { "✅ Agent Approved" }
+                   elseif ($isAgentChangesRequested) { "⚠️ Agent Changes Requested" }
+                   elseif ($isAgentReviewed) { "🤖 Agent Reviewed" }
+                   else { "" }
+
+    # Check if PR is in "Ready To Review" on the project board
+    $isReadyToReview = $readyToReviewPRNumbers -contains $pr.number
+
+    # Check if PR is approved but not merged
+    $isApproved = $pr.reviewDecision -eq "APPROVED"
+
     $processedPRs += [PSCustomObject]@{
         Number = $pr.number
         Title = $pr.title
         Author = $pr.author.login
+        Assignees = if ($pr.assignees) { ($pr.assignees | ForEach-Object { $_.login }) -join ", " } else { "" }
         Platform = Get-PRPlatform -pr $pr
         Complexity = Get-PRComplexity -pr $pr
         Milestone = if ($pr.milestone) { $pr.milestone.title } else { "" }
@@ -493,6 +617,10 @@ foreach ($pr in $allPRs) {
         IsPartner = ($labelNames -match "partner/")
         IsCommunity = ($labelNames -match "community")
         IsPriority = ($labelNames -match "p/0")
+        IsApproved = $isApproved
+        IsReadyToReview = $isReadyToReview
+        HasAgentReview = $hasAgentReview
+        AgentStatus = $agentStatus
     }
 }

@@ -514,6 +642,7 @@ foreach ($pr in $docsMauiPRs) {
         Number = $pr.number
         Title = $pr.title
         Author = $pr.author.login
+        Assignees = if ($pr.assignees) { ($pr.assignees | ForEach-Object { $_.login }) -join ", " } else { "" }
         Platform = "Docs"
         Complexity = Get-PRComplexity -pr $pr
         Milestone = if ($pr.milestone) { $pr.milestone.title } else { "" }
@@ -562,6 +691,15 @@ function Get-MilestonePriority {
 }

 # Organize PRs by category
+$approvedPRs = $processedPRs | Where-Object { $_.IsApproved } | Sort-Object {
+    Get-MilestonePriority $_.Milestone
+}, { if ($_.IsPriority) { 0 } else { 1 } }, CreatedAt
+$readyToReviewPRs = $processedPRs | Where-Object { $_.IsReadyToReview } | Sort-Object {
+    Get-MilestonePriority $_.Milestone
+}, { if ($_.IsPriority) { 0 } else { 1 } }, CreatedAt
+$agentReviewedPRList = $processedPRs | Where-Object { $_.HasAgentReview } | Sort-Object {
+    if ($_.AgentStatus -match "Approved") { 0 } elseif ($_.AgentStatus -match "Reviewed") { 1 } else { 2 }
+}, { Get-MilestonePriority $_.Milestone }, CreatedAt
 $milestonedPRs = $processedPRs | Where-Object { $_.Milestone -ne "" } | Sort-Object {
     Get-MilestonePriority $_.Milestone
 }, { if ($_.IsPriority) { 0 } else { 1 } }, CreatedAt
@@ -597,210 +735,270 @@ if ($Category -ne "all") {
         "partner" { $processedPRs = $partnerPRs }
         "community" { $processedPRs = $communityPRs }
         "recent" { $processedPRs = $recentPRs }
+        "approved" { $processedPRs = $approvedPRs }
+        "ready-to-review" { $processedPRs = $readyToReviewPRs }
+        "agent-reviewed" { $processedPRs = $agentReviewedPRList }
         "docs-maui" { $processedPRs = @() } # Will be handled separately
+        "default" {
+            $defaultPRs = @()
+            if ($priorityPRs) { $defaultPRs += @($priorityPRs) }
+            if ($milestonedPRs) { $defaultPRs += @($milestonedPRs) }
+            $processedPRs = $defaultPRs |
+                Where-Object { $_.ReviewDecision -ne "CHANGES_REQUESTED" } |
+                Sort-Object Number -Unique
+        }
     }
 }

 # Output functions
+
+# Helper to print a single PR entry (avoids repetition)
+function Write-PREntry {
+    param($pr, [string]$CategoryName, [string]$RepoOverride)
+
+    Write-Host "==="
+    Write-Host "Number:$($pr.Number)"
+    Write-Host "Title:$($pr.Title)"
+    Write-Host "URL:$($pr.URL)"
+    Write-Host "Author:$($pr.Author)"
+    if ($pr.Assignees) { Write-Host "Assignees:$($pr.Assignees)" } else { Write-Host "Assignees:⚠️ Unassigned" }
+    if ($RepoOverride) { Write-Host "Repo:$RepoOverride" } else { Write-Host "Platform:$($pr.Platform)" }
+    Write-Host "Complexity:$($pr.Complexity)"
+    Write-Host "Milestone:$($pr.Milestone)"
+    Write-Host "ReviewStatus:$($pr.ReviewStatus)"
+    if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
+    if ($pr.AgentStatus) { Write-Host "AgentReview:$($pr.AgentStatus)" } else { Write-Host "AgentReview:❌ Not Reviewed" }
+    if ($pr.IsReadyToReview) { Write-Host "BoardStatus:Ready To Review" }
+    Write-Host "Age:$($pr.Age) days"
+    Write-Host "Updated:$($pr.Updated) days ago"
+    Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
+    Write-Host "Labels:$($pr.Labels)"
+    Write-Host "Category:$CategoryName"
+}
+
 function Format-Review-Output {
     Write-Host ""
     Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

-    # Priority PRs (P/0)
-    if ($priorityPRs.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "priority")) {
-        Write-Host ""
-        Write-Host "🔴 PRIORITY (P/0) PRs - $($priorityPRs.Count) found" -ForegroundColor Red
-        Write-Host "-----------------------------------------------------------"
-        foreach ($pr in ($priorityPRs | Select-Object -First $Limit)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Platform:$($pr.Platform)"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:priority"
+    # Helper: check if a category should be displayed
+    # "default" shows only priority + milestoned; "all" shows everything
+    $showCategory = {
+        param([string]$cat)
+        if ($Category -eq $cat) { return $true }
+        if ($Category -eq "all") { return $true }
+        if ($Category -eq "default" -and ($cat -eq "priority" -or $cat -eq "milestoned")) { return $true }
+        return $false
+    }
+
+    # In default mode, only show approved or needs-review PRs (skip changes-requested)
+    $defaultFilter = {
+        param($prList)
+        if ($Category -eq "default") {
+            $prList | Where-Object { $_.ReviewDecision -ne "CHANGES_REQUESTED" }
+        } else {
+            $prList
+        }
+    }
+
+    # 1. Priority PRs (P/0) - ALWAYS on top
+    if ($priorityPRs.Count -gt 0 -and (& $showCategory "priority")) {
+        $priorityToDisplay = & $defaultFilter $priorityPRs
+        if ($priorityToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "🔴 PRIORITY (P/0) PRs - $($priorityToDisplay.Count) found" -ForegroundColor Red
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($priorityToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "priority"
+            }
         }
     }

-    # Milestoned PRs
-    if ($milestonedPRs.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "milestoned")) {
-        Write-Host ""
-        Write-Host "📅 MILESTONED PRs - $($milestonedPRs.Count) found" -ForegroundColor Yellow
-        Write-Host "-----------------------------------------------------------"
-        foreach ($pr in ($milestonedPRs | Select-Object -First $Limit)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Platform:$($pr.Platform)"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:milestoned"
+    # 2. Approved but not merged PRs
+    if ($approvedPRs.Count -gt 0 -and (& $showCategory "approved")) {
+        $approvedToDisplay = if ($Category -eq "approved") {
+            $approvedPRs
+        } else {
+            $approvedPRs | Where-Object { -not $_.IsPriority }
+        }
+        if ($approvedToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "🟢 APPROVED (NOT MERGED) PRs - $($approvedToDisplay.Count) found" -ForegroundColor Green
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($approvedToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "approved"
+            }
         }
     }

-    # Partner PRs
-    if ($partnerPRs.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "partner")) {
-        Write-Host ""
-        Write-Host "🤝 PARTNER PRs - $($partnerPRs.Count) found" -ForegroundColor Magenta
-        Write-Host "-----------------------------------------------------------"
-        foreach ($pr in ($partnerPRs | Select-Object -First $Limit)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Platform:$($pr.Platform)"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:partner"
+    # 3. Ready To Review (from project board)
+    if ($readyToReviewPRs.Count -gt 0 -and (& $showCategory "ready-to-review")) {
+        $readyToDisplay = if ($Category -eq "ready-to-review") {
+            $readyToReviewPRs
+        } else {
+            $readyToReviewPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved }
+        }
+        if ($readyToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "📋 READY TO REVIEW (Project Board) PRs - $($readyToDisplay.Count) found" -ForegroundColor Yellow
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($readyToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "ready-to-review"
+            }
         }
     }

-    # Community PRs
-    if ($communityPRs.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "community")) {
-        Write-Host ""
-        Write-Host "✨ COMMUNITY PRs - $($communityPRs.Count) found" -ForegroundColor Green
-        Write-Host "-----------------------------------------------------------"
-        foreach ($pr in ($communityPRs | Select-Object -First $Limit)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Platform:$($pr.Platform)"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:community"
+    # 4. Milestoned PRs (review these BEFORE non-milestoned agent-reviewed PRs)
+    if ($milestonedPRs.Count -gt 0 -and (& $showCategory "milestoned")) {
+        $milestonedToDisplay = if ($Category -eq "milestoned") {
+            $milestonedPRs
+        } else {
+            $milestonedPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview }
+        }
+        $milestonedToDisplay = & $defaultFilter $milestonedToDisplay
+        if ($milestonedToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "📅 MILESTONED PRs - $($milestonedToDisplay.Count) found" -ForegroundColor Yellow
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($milestonedToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "milestoned"
+            }
         }
     }

-    # Recent PRs waiting for review
-    # When Category is explicitly "recent", show ALL recent PRs
-    # When Category is "all", only show those not in other categories (to avoid duplicates)
+    # 5. Agent Reviewed PRs
+    if ($agentReviewedPRList.Count -gt 0 -and (& $showCategory "agent-reviewed")) {
+        $agentToDisplay = if ($Category -eq "agent-reviewed") {
+            $agentReviewedPRList
+        } else {
+            $agentReviewedPRList | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq "" }
+        }
+        if ($agentToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "🤖 AGENT REVIEWED PRs - $($agentToDisplay.Count) found" -ForegroundColor DarkCyan
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($agentToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "agent-reviewed"
+            }
+        }
+    }
+
+    # 6. Partner PRs
+    if ($partnerPRs.Count -gt 0 -and (& $showCategory "partner")) {
+        $partnerToDisplay = if ($Category -eq "partner") {
+            $partnerPRs
+        } else {
+            $partnerPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq "" }
+        }
+        if ($partnerToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "🤝 PARTNER PRs - $($partnerToDisplay.Count) found" -ForegroundColor Magenta
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($partnerToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "partner"
+            }
+        }
+    }
+
+    # 7. Community PRs
+    if ($communityPRs.Count -gt 0 -and (& $showCategory "community")) {
+        $communityToDisplay = if ($Category -eq "community") {
+            $communityPRs
+        } else {
+            $communityPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq "" }
+        }
+        if ($communityToDisplay.Count -gt 0) {
+            Write-Host ""
+            Write-Host "✨ COMMUNITY PRs - $($communityToDisplay.Count) found" -ForegroundColor Green
+            Write-Host "-----------------------------------------------------------"
+            foreach ($pr in ($communityToDisplay | Select-Object -First $Limit)) {
+                Write-PREntry -pr $pr -CategoryName "community"
+            }
+        }
+    }
+
+    # 8. Recent PRs waiting for review
     $recentToDisplay = if ($Category -eq "recent") {
         $recentPRs
     } else {
         $recentPRs | Where-Object {
-            -not $_.IsPriority -and -not $_.IsPartner -and -not $_.IsCommunity -and $_.Milestone -eq ""
+            -not $_.IsPriority -and -not $_.IsPartner -and -not $_.IsCommunity -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq ""
         }
     }
-    if ($recentToDisplay.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "recent")) {
+    if ($recentToDisplay.Count -gt 0 -and (& $showCategory "recent")) {
         Write-Host ""
         Write-Host "🕐 RECENT PRs WAITING FOR REVIEW (last 2 weeks) - $($recentToDisplay.Count) found" -ForegroundColor Cyan
         Write-Host "-----------------------------------------------------------"
-        $recentToShow = [Math]::Max($RecentLimit, 5)  # Always show at least 5
+        $recentToShow = [Math]::Max($RecentLimit, 5)
         foreach ($pr in ($recentToDisplay | Select-Object -First $recentToShow)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Platform:$($pr.Platform)"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:recent"
+            Write-PREntry -pr $pr -CategoryName "recent"
         }
     }

-    # docs-maui PRs - Priority
-    if ($docsMauiPriorityPRs.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "docs-maui")) {
+    # 9. docs-maui PRs - Priority
+    if ($docsMauiPriorityPRs.Count -gt 0 -and (& $showCategory "docs-maui")) {
         Write-Host ""
         Write-Host "📚 DOCS-MAUI PRIORITY PRs - $($docsMauiPriorityPRs.Count) found" -ForegroundColor Blue
         Write-Host "-----------------------------------------------------------"
         foreach ($pr in ($docsMauiPriorityPRs | Select-Object -First $DocsLimit)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Repo:docs-maui"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:docs-maui-priority"
+            Write-PREntry -pr $pr -CategoryName "docs-maui-priority" -RepoOverride "docs-maui"
         }
     }

-    # docs-maui PRs - Waiting for Review (at least 5)
-    if ($docsMauiRecentPRs.Count -gt 0 -and ($Category -eq "all" -or $Category -eq "docs-maui")) {
+    # 10. docs-maui PRs - Waiting for Review
+    if ($docsMauiRecentPRs.Count -gt 0 -and (& $showCategory "docs-maui")) {
         Write-Host ""
         Write-Host "📖 DOCS-MAUI PRs WAITING FOR REVIEW - $($docsMauiRecentPRs.Count) found" -ForegroundColor Blue
         Write-Host "-----------------------------------------------------------"
-        $docsToShow = [Math]::Max($DocsLimit, 5)  # Always show at least 5
+        $docsToShow = [Math]::Max($DocsLimit, 5)
         foreach ($pr in ($docsMauiRecentPRs | Select-Object -First $docsToShow)) {
-            Write-Host "==="
-            Write-Host "Number:$($pr.Number)"
-            Write-Host "Title:$($pr.Title)"
-            Write-Host "URL:$($pr.URL)"
-            Write-Host "Author:$($pr.Author)"
-            Write-Host "Repo:docs-maui"
-            Write-Host "Complexity:$($pr.Complexity)"
-            Write-Host "Milestone:$($pr.Milestone)"
-            Write-Host "ReviewStatus:$($pr.ReviewStatus)"
-            if ($pr.ProjectStatus) { Write-Host "ProjectStatus:$($pr.ProjectStatus)" }
-            Write-Host "Age:$($pr.Age) days"
-            Write-Host "Updated:$($pr.Updated) days ago"
-            Write-Host "Files:$($pr.Files) (+$($pr.Additions)/-$($pr.Deletions))"
-            Write-Host "Labels:$($pr.Labels)"
-            Write-Host "Category:docs-maui-waiting-for-review"
+            Write-PREntry -pr $pr -CategoryName "docs-maui-waiting-for-review" -RepoOverride "docs-maui"
         }
     }

-    # Summary
+    # Summary - show only categories that were displayed, with actual filtered/deduped counts
     Write-Host ""
     Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
-    Write-Host "SUMMARY" -ForegroundColor Cyan
-    Write-Host "  Priority (P/0): $($priorityPRs.Count)"
-    Write-Host "  Milestoned: $($milestonedPRs.Count)"
-    Write-Host "  Partner: $($partnerPRs.Count)"
-    Write-Host "  Community: $($communityPRs.Count)"
-    Write-Host "  Recent Waiting for Review (2 weeks): $($recentPRs.Count)"
-    Write-Host "  docs-maui Priority: $($docsMauiPriorityPRs.Count)"
-    Write-Host "  docs-maui Waiting for Review: $($docsMauiRecentPRs.Count)"
+    Write-Host "SUMMARY (showing: $Category)" -ForegroundColor Cyan
+    if (& $showCategory "priority") {
+        $c = @(& $defaultFilter $priorityPRs).Count
+        Write-Host "  Priority (P/0): $c"
+    }
+    if (& $showCategory "approved") {
+        $l = if ($Category -eq "approved") { $approvedPRs } else { @($approvedPRs | Where-Object { -not $_.IsPriority }) }
+        Write-Host "  Approved (not merged): $($l.Count)"
+    }
+    if (& $showCategory "ready-to-review") {
+        $l = if ($Category -eq "ready-to-review") { $readyToReviewPRs } else { @($readyToReviewPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved }) }
+        Write-Host "  Ready To Review (board): $($l.Count)"
+    }
+    if (& $showCategory "milestoned") {
+        $l = if ($Category -eq "milestoned") { $milestonedPRs } else { @($milestonedPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview }) }
+        $l = @(& $defaultFilter $l)
+        Write-Host "  Milestoned: $($l.Count)"
+    }
+    if (& $showCategory "agent-reviewed") {
+        $l = if ($Category -eq "agent-reviewed") { $agentReviewedPRList } else { @($agentReviewedPRList | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq "" }) }
+        Write-Host "  Agent Reviewed: $($l.Count)"
+    }
+    if (& $showCategory "partner") {
+        $l = if ($Category -eq "partner") { $partnerPRs } else { @($partnerPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq "" }) }
+        Write-Host "  Partner: $($l.Count)"
+    }
+    if (& $showCategory "community") {
+        $l = if ($Category -eq "community") { $communityPRs } else { @($communityPRs | Where-Object { -not $_.IsPriority -and -not $_.IsApproved -and -not $_.IsReadyToReview -and $_.Milestone -eq "" }) }
+        Write-Host "  Community: $($l.Count)"
+    }
+    if (& $showCategory "recent") { Write-Host "  Recent Waiting for Review (2 weeks): $($recentPRs.Count)" }
+    if (& $showCategory "docs-maui") { Write-Host "  docs-maui Priority: $($docsMauiPriorityPRs.Count)" }
+    if (& $showCategory "docs-maui") { Write-Host "  docs-maui Waiting for Review: $($docsMauiRecentPRs.Count)" }
 }

 function Format-Json-Output {
     $output = @{
         Priority = $priorityPRs | Select-Object -First $Limit
+        Approved = $approvedPRs | Select-Object -First $Limit
+        ReadyToReview = $readyToReviewPRs | Select-Object -First $Limit
+        AgentReviewed = $agentReviewedPRList | Select-Object -First $Limit
         Milestoned = $milestonedPRs | Select-Object -First $Limit
         Partner = $partnerPRs | Select-Object -First $Limit
         Community = $communityPRs | Select-Object -First $Limit

PATCH

echo "Patch applied successfully."
