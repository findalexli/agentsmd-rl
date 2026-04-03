#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if [ -f ".github/skills/pr-build-status/SKILL.md" ]; then
    echo "Patch already applied."
    exit 0
fi

mkdir -p .github/skills/pr-build-status/scripts

# --- SKILL.md ---
cat <<'SKILLEOF' > .github/skills/pr-build-status/SKILL.md
---
name: pr-build-status
description: "Retrieve Azure DevOps build information for GitHub Pull Requests, including build IDs, stage status, and failed jobs."
metadata:
  author: dotnet-maui
  version: "1.0"
compatibility: Requires GitHub CLI (gh) authenticated with access to dotnet/maui repository.
---

# PR Build Status Skill

Retrieve Azure DevOps build information for GitHub Pull Requests.

## Tools Required

This skill uses `bash` together with `pwsh` (PowerShell 7+) to run the PowerShell scripts. No file editing or other tools are required.

## When to Use

- User asks about CI/CD status for a PR
- User asks about failed checks or builds
- User asks "what's failing on PR #XXXXX"
- User wants to see test results

## Scripts

All scripts are in `.github/skills/pr-build-status/scripts/`

### 1. Get Build IDs for a PR
```bash
pwsh .github/skills/pr-build-status/scripts/Get-PrBuildIds.ps1 -PrNumber <PR_NUMBER>
```

### 2. Get Build Status
```bash
pwsh .github/skills/pr-build-status/scripts/Get-BuildInfo.ps1 -BuildId <BUILD_ID>
# For failed jobs only:
pwsh .github/skills/pr-build-status/scripts/Get-BuildInfo.ps1 -BuildId <BUILD_ID> -FailedOnly
```

### 3. Get Build Errors and Test Failures
```bash
# Get all errors (build errors + test failures)
pwsh .github/skills/pr-build-status/scripts/Get-BuildErrors.ps1 -BuildId <BUILD_ID>

# Get only build/compilation errors
pwsh .github/skills/pr-build-status/scripts/Get-BuildErrors.ps1 -BuildId <BUILD_ID> -ErrorsOnly

# Get only test failures
pwsh .github/skills/pr-build-status/scripts/Get-BuildErrors.ps1 -BuildId <BUILD_ID> -TestsOnly
```

## Workflow

1. Get build IDs: `scripts/Get-PrBuildIds.ps1 -PrNumber XXXXX`
2. For each build, get status: `scripts/Get-BuildInfo.ps1 -BuildId YYYYY`
3. For failed builds, get error details: `scripts/Get-BuildErrors.ps1 -BuildId YYYYY`

## Prerequisites

- `gh` (GitHub CLI) - authenticated
- `pwsh` (PowerShell 7+)
SKILLEOF

# --- Get-PrBuildIds.ps1 ---
cat <<'PS1EOF' > .github/skills/pr-build-status/scripts/Get-PrBuildIds.ps1
<#
.SYNOPSIS
    Retrieves Azure DevOps build IDs associated with a GitHub PR.

.DESCRIPTION
    Queries GitHub PR checks and extracts the Azure DevOps build IDs,
    pipeline names, states, and links for each unique build.

.PARAMETER PrNumber
    The GitHub Pull Request number.

.PARAMETER Repo
    The GitHub repository in 'owner/repo' format. Defaults to 'dotnet/maui'.

.EXAMPLE
    ./Get-PrBuildIds.ps1 -PrNumber 33251

.EXAMPLE
    ./Get-PrBuildIds.ps1 -PrNumber 33251 -Repo "dotnet/maui"

.OUTPUTS
    Array of objects with Pipeline, BuildId, State, and Link properties.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [int]$PrNumber,

    [Parameter(Mandatory = $false)]
    [string]$Repo = "dotnet/maui"
)

$ErrorActionPreference = "Stop"

# Validate prerequisites
if (-not (Get-Command "gh" -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
    exit 1
}

# Get PR checks from GitHub
$checksJson = gh pr checks $PrNumber --repo $Repo --json name,link,state 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to get PR checks: $checksJson"
    exit 1
}

$checks = $checksJson | ConvertFrom-Json

# Filter to Azure DevOps checks and extract build IDs
$builds = $checks | Where-Object { $_.link -match "dev\.azure\.com" } | ForEach-Object {
    $buildId = if ($_.link -match "buildId=(\d+)") { $matches[1] } else { $null }
    $pipeline = ($_.name -split " ")[0]

    [PSCustomObject]@{
        Pipeline = $pipeline
        BuildId  = $buildId
        State    = $_.state
        Link     = $_.link
    }
} | Sort-Object -Property Pipeline, BuildId -Unique

$builds
PS1EOF

# --- Get-BuildInfo.ps1 ---
cat <<'PS1EOF' > .github/skills/pr-build-status/scripts/Get-BuildInfo.ps1
<#
.SYNOPSIS
    Retrieves detailed status information for an Azure DevOps build.

.DESCRIPTION
    Queries the Azure DevOps build timeline API and returns comprehensive
    information about the build including all stages, their status, and
    any failed or canceled jobs.

.PARAMETER BuildId
    The Azure DevOps build ID.

.PARAMETER Org
    The Azure DevOps organization. Defaults to 'dnceng-public'.

.PARAMETER Project
    The Azure DevOps project. Defaults to 'public'.

.PARAMETER FailedOnly
    If specified, only returns failed or canceled stages and jobs.

.EXAMPLE
    ./Get-BuildInfo.ps1 -BuildId 1240455

.EXAMPLE
    ./Get-BuildInfo.ps1 -BuildId 1240455 -FailedOnly

.EXAMPLE
    ./Get-BuildInfo.ps1 -BuildId 1240455 -Org "dnceng-public" -Project "public"

.OUTPUTS
    Object with BuildId, Status, Result, Stages, and FailedJobs properties.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$BuildId,

    [Parameter(Mandatory = $false)]
    [string]$Org = "dnceng-public",

    [Parameter(Mandatory = $false)]
    [string]$Project = "public",

    [Parameter(Mandatory = $false)]
    [switch]$FailedOnly
)

$ErrorActionPreference = "Stop"

# Get build info
$buildUrl = "https://dev.azure.com/$Org/$Project/_apis/build/builds/${BuildId}?api-version=7.0"
$timelineUrl = "https://dev.azure.com/$Org/$Project/_apis/build/builds/$BuildId/timeline?api-version=7.0"

try {
    $build = Invoke-RestMethod -Uri $buildUrl -Method Get -ContentType "application/json"
    $timeline = Invoke-RestMethod -Uri $timelineUrl -Method Get -ContentType "application/json"
}
catch {
    Write-Error "Failed to query Azure DevOps API: $_"
    exit 1
}

# Extract stages
$stages = $timeline.records | Where-Object { $_.type -eq "Stage" } | ForEach-Object {
    [PSCustomObject]@{
        Name   = $_.name
        State  = $_.state
        Result = $_.result
    }
} | Sort-Object -Property { $_.State -eq "completed" }, { $_.State -eq "inProgress" }

# Extract failed/canceled jobs
$failedJobs = $timeline.records |
    Where-Object {
        ($_.type -eq "Stage" -or $_.type -eq "Job") -and
        ($_.result -eq "failed" -or $_.result -eq "canceled")
    } |
    ForEach-Object {
        [PSCustomObject]@{
            Name   = $_.name
            Type   = $_.type
            Result = $_.result
        }
    } | Sort-Object -Property Type, Name

if ($FailedOnly) {
    $failedJobs
}
else {
    [PSCustomObject]@{
        BuildId    = $BuildId
        BuildNumber = $build.buildNumber
        Status     = $build.status
        Result     = $build.result
        Pipeline   = $build.definition.name
        StartTime  = $build.startTime
        FinishTime = $build.finishTime
        Stages     = $stages
        FailedJobs = $failedJobs
        Link       = "https://dev.azure.com/$Org/$Project/_build/results?buildId=$BuildId"
    }
}
PS1EOF

# --- Get-BuildErrors.ps1 ---
cat <<'PS1EOF' > .github/skills/pr-build-status/scripts/Get-BuildErrors.ps1
<#
.SYNOPSIS
    Retrieves build errors and test failures from an Azure DevOps build.

.DESCRIPTION
    Queries the Azure DevOps build timeline to find failed jobs and tasks,
    then extracts build errors (MSBuild errors, compilation failures) and
    test failures with their details.

.PARAMETER BuildId
    The Azure DevOps build ID.

.PARAMETER Org
    The Azure DevOps organization. Defaults to 'dnceng-public'.

.PARAMETER Project
    The Azure DevOps project. Defaults to 'public'.

.PARAMETER TestsOnly
    If specified, only returns test results (no build errors).

.PARAMETER ErrorsOnly
    If specified, only returns build errors (no test results).

.PARAMETER JobFilter
    Optional filter to match job/task names (supports wildcards).

.EXAMPLE
    ./Get-BuildErrors.ps1 -BuildId 1240456

.EXAMPLE
    ./Get-BuildErrors.ps1 -BuildId 1240456 -ErrorsOnly

.EXAMPLE
    ./Get-BuildErrors.ps1 -BuildId 1240456 -TestsOnly -JobFilter "*SafeArea*"

.OUTPUTS
    Objects with Type (BuildError/TestFailure), Source, Message, and Details properties.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$BuildId,

    [Parameter(Mandatory = $false)]
    [string]$Org = "dnceng-public",

    [Parameter(Mandatory = $false)]
    [string]$Project = "public",

    [Parameter(Mandatory = $false)]
    [switch]$TestsOnly,

    [Parameter(Mandatory = $false)]
    [switch]$ErrorsOnly,

    [Parameter(Mandatory = $false)]
    [string]$JobFilter
)

$ErrorActionPreference = "Stop"

# Get build timeline
$timelineUrl = "https://dev.azure.com/$Org/$Project/_apis/build/builds/${BuildId}/timeline?api-version=7.0"

try {
    $timeline = Invoke-RestMethod -Uri $timelineUrl -Method Get -ContentType "application/json"
}
catch {
    Write-Error "Failed to query Azure DevOps timeline API: $_"
    exit 1
}

$allResults = @()

# --- SECTION 1: Find Build Errors from Failed Tasks ---
if (-not $TestsOnly) {
    $failedTasks = $timeline.records | Where-Object {
        $_.type -eq "Task" -and
        $_.result -eq "failed" -and
        $_.log.url -and
        (-not $JobFilter -or $_.name -like $JobFilter)
    }

    foreach ($task in $failedTasks) {
        Write-Host "Analyzing failed task: $($task.name)" -ForegroundColor Red

        try {
            $log = Invoke-RestMethod -Uri $task.log.url -Method Get
            $lines = $log -split "`n"

            # Find MSBuild errors and ##[error] markers
            $errorLines = $lines | Where-Object {
                $_ -match ": error [A-Z]+\d*:" -or      # MSBuild errors (CS1234, MT1234, etc.)
                $_ -match ": Error :" -or               # Xamarin.Shared.Sdk errors
                $_ -match "##\[error\]"                 # Azure DevOps error markers
            }

            foreach ($errorLine in $errorLines) {
                # Clean up the line
                $cleanLine = $errorLine -replace "^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", ""
                $cleanLine = $cleanLine -replace "##\[error\]", ""

                # Skip generic "exited with code" errors - we want the actual error
                if ($cleanLine -match "exited with code") {
                    continue
                }

                $allResults += [PSCustomObject]@{
                    Type    = "BuildError"
                    Source  = $task.name
                    Message = $cleanLine.Trim()
                    Details = ""
                }
            }
        }
        catch {
            Write-Warning "Failed to fetch log for task $($task.name): $_"
        }
    }
}

# --- SECTION 2: Find Test Failures from Jobs ---
if (-not $ErrorsOnly) {
    $jobs = $timeline.records | Where-Object {
        $_.type -eq "Job" -and
        $_.log.url -and
        $_.state -eq "completed" -and
        $_.result -eq "failed" -and
        (-not $JobFilter -or $_.name -like $JobFilter)
    }

    foreach ($job in $jobs) {
        Write-Host "Analyzing job for test failures: $($job.name)" -ForegroundColor Yellow

        try {
            $logContent = Invoke-RestMethod -Uri $job.log.url -Method Get
            $lines = $logContent -split "`n"

            # Find test result lines: "Failed <TestName> [duration]"
            for ($i = 0; $i -lt $lines.Count; $i++) {
                if ($lines[$i] -match "^\d{4}-\d{2}-\d{2}.*\s+Failed\s+(\S+)\s+\[([^\]]+)\]") {
                    $testName = $matches[1]
                    $duration = $matches[2]

                    $errorMessage = ""
                    $stackTrace = ""

                    # Look ahead for error message and stack trace
                    for ($j = $i + 1; $j -lt $lines.Count; $j++) {
                        $line = $lines[$j]
                        $cleanLine = $line -replace "^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", ""

                        if ($cleanLine -match "^\s*Error Message:") {
                            for ($k = $j + 1; $k -lt [Math]::Min($j + 10, $lines.Count); $k++) {
                                $msgLine = $lines[$k] -replace "^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", ""
                                if ($msgLine -match "^\s*Stack Trace:" -or [string]::IsNullOrWhiteSpace($msgLine)) {
                                    break
                                }
                                $errorMessage += $msgLine.Trim() + " "
                            }
                        }

                        if ($cleanLine -match "^\s*Stack Trace:") {
                            for ($k = $j + 1; $k -lt [Math]::Min($j + 5, $lines.Count); $k++) {
                                $stLine = $lines[$k] -replace "^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", ""
                                if ($stLine -match "at .+ in .+:line \d+") {
                                    $stackTrace = $stLine.Trim()
                                    break
                                }
                            }
                            break
                        }

                        # Stop if we hit the next test
                        if ($cleanLine -match "^\s*(Passed|Failed|Skipped)\s+\S+\s+\[") {
                            break
                        }
                    }

                    $allResults += [PSCustomObject]@{
                        Type    = "TestFailure"
                        Source  = $job.name
                        Message = $testName
                        Details = if ($errorMessage) { "$errorMessage`n$stackTrace".Trim() } else { $stackTrace }
                    }
                }
            }
        }
        catch {
            Write-Warning "Failed to fetch log for job $($job.name): $_"
        }
    }
}

# Remove duplicate errors (same message from same source)
$uniqueResults = $allResults | Group-Object -Property Type, Source, Message | ForEach-Object {
    $_.Group | Select-Object -First 1
}

# Summary
$buildErrors = ($uniqueResults | Where-Object { $_.Type -eq "BuildError" }).Count
$testFailures = ($uniqueResults | Where-Object { $_.Type -eq "TestFailure" }).Count

Write-Host "`nSummary: $buildErrors build error(s), $testFailures test failure(s)" -ForegroundColor Cyan

$uniqueResults
PS1EOF

echo "Patch applied successfully."
