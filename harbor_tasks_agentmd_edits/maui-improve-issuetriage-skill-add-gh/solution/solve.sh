#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'Common Mistakes to Avoid' .github/skills/issue-triage/SKILL.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- SKILL.md: update version, add prerequisites, workflow docs, common mistakes ---
cat > /tmp/skill_patch.py << 'PYEOF'
from pathlib import Path

skill = Path(".github/skills/issue-triage/SKILL.md")
content = skill.read_text()

# 1. Update version 2.1 -> 2.3 and compatibility line
content = content.replace('version: "2.1"', 'version: "2.3"')
content = content.replace(
    'compatibility: Requires GitHub CLI (gh) authenticated with access to dotnet/maui repository.',
    'compatibility: Requires GitHub CLI (gh) installed and authenticated. Run `gh auth login` before using.'
)

# 2. Add Prerequisites section after "5. Tracking progress through a triage session"
prereq = """
## Prerequisites

**GitHub CLI (gh) must be installed and authenticated:**

```bash
# Install
# Windows:
winget install --id GitHub.cli

# macOS:
brew install gh

# Linux:
# See https://cli.github.com/manual/installation

# Authenticate (required before first use)
gh auth login
```

The scripts will check for `gh` and exit with installation instructions if not found.
"""
content = content.replace(
    "5. Tracking progress through a triage session\n\n## When to Use",
    "5. Tracking progress through a triage session\n" + prereq + "\n## When to Use"
)

# 3. Add critical rule before Step 1
content = content.replace(
    "## Triage Workflow\n\n### Step 1",
    "## Triage Workflow\n\n**\U0001f6a8 CRITICAL: ALWAYS use the skill scripts. NEVER use ad-hoc GitHub API queries.**\n\nThe scripts have proper filters, exclusions, and milestone logic built-in. Don't bypass them.\n\n### Step 1"
)

# 4. Add "What this does" after init step
content = content.replace(
    '```\n\n### Step 2: Load Issues Into Memory',
    '```\n\n**What this does:**\n- Fetches current milestones (SR4, SR5, etc.) from GitHub API\n- Displays servicing milestones for reference during triage\n- Creates session file to track progress\n\n### Step 2: Load Issues Into Memory'
)

# 5. Replace Step 2 content
old_step2 = """### Step 2: Load Issues Into Memory

Load a batch of issues (e.g., 20) but DO NOT display them all. Store them for one-at-a-time presentation:

```bash
pwsh .github/skills/issue-triage/scripts/query-issues.ps1 -Limit 100 -OutputFormat triage
```"""

new_step2 = """### Step 2: Load Issues Into Memory

**MANDATORY: Use query-issues.ps1 - it has the right filters!**

```bash
pwsh .github/skills/issue-triage/scripts/query-issues.ps1 -Limit 50 -OutputFormat triage
```

**What this does:**
- Queries GitHub with exclusion filters: `-label:s/needs-info -label:s/needs-repro -label:area-blazor -label:s/try-latest-version -label:s/move-to-vs-feedback`
- Returns issues without milestones
- Stores results for one-at-a-time presentation

**DON'T:**
- \u274c Use `github-mcp-server-list_issues` directly
- \u274c Use `github-mcp-server-search_issues` without the same filters
- \u274c Try to replicate the logic yourself - use the script!"""

content = content.replace(old_step2, new_step2)

# 6. Fix suggestion line
content = content.replace(
    '**My Suggestion**: `Milestone` - Reason',
    '**My Suggestion**: `Milestone` - Reason (based on init session output)'
)

# 7. Update Step 4 milestone examples
content = content.replace(
    '- A milestone name (e.g., "Backlog", "current SR", "Servicing")',
    '- A milestone name (e.g., "Backlog", ".NET 10 SR5", ".NET 10 Servicing")'
)

# 8. Replace Step 5 and add Step 6
old_step5 = """### Step 5: Apply Changes and Move to Next

After applying changes, automatically present the NEXT issue."""

new_step5 = """### Step 5: Move to Next Issue

After user decision, automatically present the NEXT issue.

### Step 6: When Batch is Empty

**\U0001f6a8 CRITICAL: When you run out of issues, AUTOMATICALLY reload more issues.**

```bash
# Run query again to load next batch
pwsh .github/skills/issue-triage/scripts/query-issues.ps1 -Limit 50 -Skip <current_count> -OutputFormat triage
```

**DO NOT:**
- \u274c Stop and ask "Load more?"
- \u274c Say "No more issues found"
- \u274c Use different GitHub queries

**DO:**
- \u2705 Automatically run `query-issues.ps1` again with `-Skip` parameter
- \u2705 Continue presenting issues one at a time
- \u2705 Only stop when query returns zero issues"""

content = content.replace(old_step5, new_step5)

# 9. Replace Milestone Suggestion Logic section
old_milestone = """## Milestone Suggestion Logic

The script dynamically queries current milestones from dotnet/maui and suggests them based on issue characteristics:

| Condition | Suggested Milestone | Reason |
|-----------|---------------------|--------|
| Linked PR has milestone | PR's milestone | "PR already has milestone" |
| Has `i/regression` label | Current SR milestone (soonest due) | "Regression - current SR milestone" |
| Has open linked PR | Servicing milestone (or next SR) | "Has open PR" |
| Default | Backlog | "No PR, not a regression" |

**Note**: SR milestones are sorted by due date, so the soonest SR is suggested for regressions. Milestone names change monthly, so they are queried dynamically rather than hardcoded."""

new_milestone = """## Milestone Suggestion Logic

**\U0001f6a8 CRITICAL: ALWAYS use actual milestone names from init-triage-session.ps1 output. NEVER guess or assume milestone names.**

The skill dynamically queries current milestones from dotnet/maui at session initialization. Milestone names change frequently (e.g., SR4, SR5, SR6), so **always reference the session output** when suggesting milestones.

### Suggestion Guidelines

| Condition | Suggested Milestone | Reason |
|-----------|---------------------|--------|
| Linked PR has milestone | PR's milestone | "PR already has milestone" |
| Has `i/regression` label | Highest numbered SR milestone | "Regression - needs servicing" |
| Has open linked PR | Current servicing milestone | "Has open PR" |
| Default | Backlog | "No PR, not a regression" |

**Example Session Output:**
```
Servicing Releases:
  - .NET 9 Servicing [246 open]
  - .NET 10 Servicing [213 open]
  - .NET 10 SR5 [55 open]         \u2190 Use this for .NET 10 regressions
  - .NET 10.0 SR4 [103 open]

Other:
  - .NET 11 Planning [167 open]
  - .NET 11.0-preview1 [8 open]

Backlog:
  - Backlog [3037 open]
```

**How to suggest milestones:**
- \u2705 "Assign to `.NET 10 SR5`" (from session output)
- \u274c "Assign to `.NET 10 SR2`" (guessing, might not exist)
- \u274c "Assign to current SR" (ambiguous, multiple active)"""

content = content.replace(old_milestone, new_milestone)

# 10. Remove old "Common Milestone Types" section
old_common = """## Common Milestone Types

| Milestone Type | Use When |
|----------------|----------|
| Current SR (e.g., SR3) | Regressions, critical bugs with PRs ready |
| Next SR (e.g., SR4) | Important bugs, regressions being investigated |
| Servicing | General fixes with PRs, non-urgent improvements |
| Backlog | No PR, not a regression, nice-to-have fixes |

**Note**: Use `init-triage-session.ps1` to see current milestone names.

## Label Quick Reference"""
new_common = """## Label Quick Reference"""
content = content.replace(old_common, new_common)

# 11. Add Common Mistakes section before Session Tracking
mistakes = """
## Common Mistakes to Avoid

| Mistake | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| \u274c Using `github-mcp-server-list_issues` directly | Missing exclusion filters (needs-info, needs-repro, etc.) | \u2705 Use `query-issues.ps1` script |
| \u274c Stopping when batch is empty | There are likely more issues available | \u2705 Automatically run `query-issues.ps1 -Skip N` |
| \u274c Suggesting milestone names like "SR2" | Milestone doesn't exist, based on assumptions | \u2705 Use actual milestone names from `init-triage-session.ps1` output |
| \u274c Asking "Load more?" when out of issues | Creates unnecessary interruption | \u2705 Just load more automatically |
| \u274c Using ad-hoc API queries with custom filters | Likely to miss or include wrong issues | \u2705 Trust the skill's scripts - they have the right logic |

"""
content = content.replace(
    "## Session Tracking (Optional)",
    mistakes + "## Session Tracking (Optional)"
)

skill.write_text(content)
print("SKILL.md patched")
PYEOF
python3 /tmp/skill_patch.py

# --- init-triage-session.ps1: add gh check + Invoke-RestMethod ---
INIT_SCRIPT=".github/skills/issue-triage/scripts/init-triage-session.ps1"

python3 - "$INIT_SCRIPT" << 'PYEOF'
import sys
from pathlib import Path

f = Path(sys.argv[1])
content = f.read_text()

# Insert gh check after the banner
gh_check = '''
# Check for GitHub CLI prerequisite
Write-Host ""
Write-Host "Checking prerequisites..." -ForegroundColor Cyan
try {
    $ghPath = (Get-Command gh -ErrorAction Stop).Source
    Write-Host "  \u2705 GitHub CLI found: $ghPath" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "  \u274c GitHub CLI (gh) is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "  The issue-triage skill requires GitHub CLI for querying issues." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Installation:" -ForegroundColor Cyan
    Write-Host "    Windows:  winget install --id GitHub.cli" -ForegroundColor White
    Write-Host "    macOS:    brew install gh" -ForegroundColor White
    Write-Host "    Linux:    See https://cli.github.com/manual/installation" -ForegroundColor White
    Write-Host ""
    Write-Host "  After installation, authenticate with: gh auth login" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Verify GitHub CLI authentication
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  \u274c GitHub CLI (gh) is not authenticated" -ForegroundColor Red
    Write-Host "  Run: gh auth login" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
Write-Host "  \u2705 GitHub CLI authenticated" -ForegroundColor Green
'''

marker = 'Write-Host "\u2559\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d" -ForegroundColor Cyan'
content = content.replace(marker, marker + "\n" + gh_check, 1)

# Replace gh api milestone fetching with Invoke-RestMethod
old_ms = """    $msResult = gh api repos/dotnet/maui/milestones --jq '.[] | {number, title, due_on, open_issues}' 2>&1
    $msLines = $msResult -split "`n" | Where-Object { $_ -match "^\\{" }

    foreach ($line in $msLines) {
        $ms = $line | ConvertFrom-Json"""

new_ms = """    $msData = Invoke-RestMethod -Uri "https://api.github.com/repos/dotnet/maui/milestones?state=open&per_page=100"

    foreach ($ms in $msData) {"""

content = content.replace(old_ms, new_ms)

f.write_text(content)
print("init-triage-session.ps1 patched")
PYEOF

# --- query-issues.ps1: add gh check ---
QUERY_SCRIPT=".github/skills/issue-triage/scripts/query-issues.ps1"

python3 - "$QUERY_SCRIPT" << 'PYEOF'
import sys
from pathlib import Path

f = Path(sys.argv[1])
content = f.read_text()

gh_check = '''# Check for GitHub CLI prerequisite
try {
    $null = Get-Command gh -ErrorAction Stop
} catch {
    Write-Host ""
    Write-Host "\u274c GitHub CLI (gh) is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "The issue-triage skill requires GitHub CLI for querying issues." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installation:" -ForegroundColor Cyan
    Write-Host "  Windows:  winget install --id GitHub.cli" -ForegroundColor White
    Write-Host "  macOS:    brew install gh" -ForegroundColor White
    Write-Host "  Linux:    See https://cli.github.com/manual/installation" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, authenticate with: gh auth login" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Verify GitHub CLI authentication
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "\u274c GitHub CLI (gh) is not authenticated" -ForegroundColor Red
    Write-Host "Run: gh auth login" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
Write-Host "\u2705 GitHub CLI authenticated" -ForegroundColor Green

'''

marker = 'Write-Host "Querying GitHub issues..." -ForegroundColor Cyan'
content = content.replace(marker, gh_check + marker)

f.write_text(content)
print("query-issues.ps1 patched")
PYEOF

echo "Patch applied successfully."
