#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'function Write-Warn' .github/scripts/shared/shared-utils.ps1 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/agents/pr/PLAN-TEMPLATE.md b/.github/agents/pr/PLAN-TEMPLATE.md
index 1ee1bbc54b65..11901d56dd91 100644
--- a/.github/agents/pr/PLAN-TEMPLATE.md
+++ b/.github/agents/pr/PLAN-TEMPLATE.md
@@ -57,7 +57,7 @@ See `SHARED-RULES.md` for complete details. Key points:
 
 **Round 1: Run try-fix with each model (SEQUENTIAL)**
 - [ ] claude-sonnet-4.5
-- [ ] claude-opus-4.5
+- [ ] claude-opus-4.6
 - [ ] gpt-5.2
 - [ ] gpt-5.2-codex
 - [ ] gemini-3-pro-preview
@@ -68,10 +68,10 @@ See `SHARED-RULES.md` for complete details. Key points:
 - [ ] Invoke EACH model: "Any NEW fix ideas?"
 - [ ] Record responses in Cross-Pollination table
 - [ ] Run try-fix for new ideas (SEQUENTIAL)
-- [ ] Repeat until ALL 5 say "NO NEW IDEAS" (max 3 rounds)
+- [ ] Repeat until ALL 6 say "NO NEW IDEAS" (max 3 rounds)
 
 **Completion:**
-- [ ] Cross-Pollination table has all 5 responses
+- [ ] Cross-Pollination table has all 6 responses
 - [ ] Mark Exhausted: Yes
 - [ ] Compare passing candidates with PR's fix
 - [ ] Select best fix (results → simplicity → robustness)
diff --git a/.github/agents/pr/SHARED-RULES.md b/.github/agents/pr/SHARED-RULES.md
index 8dc2e0fe18ef..70662faccd9b 100644
--- a/.github/agents/pr/SHARED-RULES.md
+++ b/.github/agents/pr/SHARED-RULES.md
@@ -132,7 +132,7 @@ Phase 4 uses these 5 AI models for try-fix exploration (run SEQUENTIALLY):
 | Order | Model |
 |-------|-------|
 | 1 | `claude-sonnet-4.5` |
-| 2 | `claude-opus-4.5` |
+| 2 | `claude-opus-4.6` |
 | 3 | `gpt-5.2` |
 | 4 | `gpt-5.2-codex` |
 | 5 | `gemini-3-pro-preview` |
diff --git a/.github/agents/pr/post-gate.md b/.github/agents/pr/post-gate.md
index 16c5fc8e3272..f030801ee257 100644
--- a/.github/agents/pr/post-gate.md
+++ b/.github/agents/pr/post-gate.md
@@ -24,6 +24,16 @@ If Gate is not passed, go back to `.github/agents/pr.md` and complete phases 1-2
 
 If try-fix cannot run due to environment issues, **STOP and ask the user**. Do NOT mark attempts as "BLOCKED" and continue.
 
+### 🚨 CRITICAL: Stop on Environment Blockers (Applies to Phase 4)
+
+The same "Stop on Environment Blockers" rule from `pr.md` applies here. If try-fix cannot run due to:
+- Missing Appium drivers
+- Device/emulator not available
+- WinAppDriver not installed
+- Platform tools missing
+
+**STOP and ask the user** before continuing. Do NOT mark try-fix attempts as "BLOCKED" and continue. Either fix the environment issue or get explicit user permission to skip.
+
 ---
 
 ## 🔧 FIX: Explore and Select Fix (Phase 3)
@@ -52,7 +62,7 @@ Phase 4 uses a **multi-model approach** to maximize fix diversity. Each AI model
 
 #### Round 1: Run try-fix with Each Model
 
-Run the `try-fix` skill **5 times sequentially**, once with each model (see `SHARED-RULES.md` for model list).
+Run the `try-fix` skill **6 times sequentially**, once with each model (see `SHARED-RULES.md` for model list).
 
 **For each model**, invoke the try-fix skill:
 ```
@@ -70,6 +80,23 @@ Generate ONE independent fix idea. Review the PR's fix first to ensure your appr
 
 **Wait for each to complete before starting the next.**
 
+**🧹 MANDATORY: Clean up between attempts.** After each try-fix completes (pass or fail), run these commands before starting the next attempt:
+
+```bash
+# 1. Restore any baseline state from the previous attempt (safe no-op if none exists)
+pwsh .github/scripts/EstablishBrokenBaseline.ps1 -Restore
+
+# 2. Restore all tracked files to HEAD (the merged PR state)
+# This catches any files the previous attempt modified but didn't restore
+git checkout HEAD -- .
+
+# 3. Remove untracked files added by the previous attempt
+# git checkout restores tracked files but does NOT remove new untracked files
+git clean -fd --exclude=CustomAgentLogsTmp/
+```
+
+**Why this is required:** Each try-fix attempt modifies source files. If an attempt fails mid-way (build error, timeout, model error), it may not run its own cleanup step. Without explicit cleanup, the next attempt starts with a dirty working tree, which can cause missing files, corrupt state, or misleading test results. Use `HEAD` (not just `-- .`) to also restore deleted files.
+
 #### Round 2+: Cross-Pollination Loop (MANDATORY)
 
 After Round 1, invoke EACH of the 5 models to ask for new ideas. **No shortcuts allowed.**
@@ -77,7 +104,7 @@ After Round 1, invoke EACH of the 5 models to ask for new ideas. **No shortcuts
 **❌ WRONG**: Using `explore`/`glob`, declaring exhaustion without invoking each model
 **✅ CORRECT**: Invoke EACH model via task agent and ask explicitly
 
-**Steps (repeat until all 5 say "NO NEW IDEAS", max 3 rounds):**
+**Steps (repeat until all 6 say "NO NEW IDEAS", max 3 rounds):**
 
 1. **Compile bounded summary** (max 3-4 bullets per attempt):
    - Attempt #, approach (1 line), result (✅/❌), key learning (1 line)
@@ -176,7 +203,7 @@ Update the state file:
   | Model | Round 2 Response |
   |-------|------------------|
   | claude-sonnet-4.5 | NO NEW IDEAS |
-  | claude-opus-4.5 | NO NEW IDEAS |
+  | claude-opus-4.6 | NO NEW IDEAS |
   | gpt-5.2 | NO NEW IDEAS |
   | gpt-5.2-codex | NO NEW IDEAS |
   | gemini-3-pro-preview | NO NEW IDEAS |
@@ -298,3 +325,44 @@ Update all phase statuses to complete.
 - ❌ **Forgetting to revert between attempts** - Each try-fix must start from broken baseline, end with PR restored
 - ❌ **Declaring exhaustion prematurely** - All 5 models must confirm "no new ideas" via actual invocation
 - ❌ **Rushing the report** - Take time to write clear justification
+- ❌ **Skipping cleanup between attempts** - ALWAYS run `-Restore` + `git checkout HEAD -- .` + `git clean -fd --exclude=CustomAgentLogsTmp/` between try-fix attempts (see Step 1)
+
+---
+
+## Common Errors and Recovery
+
+### skill(try-fix) fails with "ENOENT: no such file or directory"
+
+**Symptom:** `skill(try-fix) Failed to read skill file: Error: ENOENT: no such file or directory, open '.../.github/skills/try-fix/SKILL.md'`
+
+**Root cause:** A previous try-fix attempt failed mid-way and left the working tree in a dirty state. Files may have been modified or deleted by `EstablishBrokenBaseline.ps1` without being restored.
+
+**Fix:** Run cleanup before retrying:
+```bash
+pwsh .github/scripts/EstablishBrokenBaseline.ps1 -Restore
+git checkout HEAD -- .
+git clean -fd --exclude=CustomAgentLogsTmp/
+```
+
+Then retry the try-fix attempt. The skill file should now be accessible.
+
+**Prevention:** Always run the cleanup commands between try-fix attempts (see Step 1).
+
+### try-fix attempt starts with dirty working tree
+
+**Symptom:** `git status` shows modified files before the attempt starts, or the build fails with unexpected errors from files the attempt didn't touch.
+
+**Root cause:** Previous attempt didn't restore its changes (crashed, timed out, or model didn't follow Step 8 restore instructions).
+
+**Fix:** Same as above — run `-Restore` + `git checkout HEAD -- .` + `git clean -fd --exclude=CustomAgentLogsTmp/` to reset to the merged PR state.
+
+### Build errors unrelated to the fix being attempted
+
+**Symptom:** Build fails with errors in files the try-fix attempt didn't modify (e.g., XAML parse errors, unrelated compilation failures).
+
+**Root cause:** Often caused by dirty working tree from a previous attempt. Can also be transient environment issues.
+
+**Fix:**
+1. Run cleanup: `pwsh .github/scripts/EstablishBrokenBaseline.ps1 -Restore && git checkout HEAD -- . && git clean -fd --exclude=CustomAgentLogsTmp/`
+2. Retry the attempt
+3. If it fails again with the same unrelated error, treat this as an environment/worktree blocker: STOP the try-fix workflow, do NOT continue with the next model, and ask the user to investigate (see "Stop on Environment Blockers").
diff --git a/.github/scripts/BuildAndRunHostApp.ps1 b/.github/scripts/BuildAndRunHostApp.ps1
index 2a7f6a31d6b7..c6103609de46 100644
--- a/.github/scripts/BuildAndRunHostApp.ps1
+++ b/.github/scripts/BuildAndRunHostApp.ps1
@@ -262,8 +262,8 @@ if ($Platform -eq "catalyst") {
         
         Write-Success "MacCatalyst app prepared (Appium will launch with test name)"
     } else {
-        Write-Warning "MacCatalyst app not found at: $appPath"
-        Write-Warning "Test may use wrong app bundle if another version is registered"
+        Write-Warn "MacCatalyst app not found at: $appPath"
+        Write-Warn "Test may use wrong app bundle if another version is registered"
     }
     
     # Set log file path directly - app will write ILogger output here
@@ -323,7 +323,7 @@ if ($Platform -eq "android") {
     & adb -s $DeviceUdid logcat -d | Select-String "com.microsoft.maui.uitests|DOTNET" > $deviceLogFile
     
     if ((Get-Item $deviceLogFile).Length -eq 0) {
-        Write-Warning "No logs found for com.microsoft.maui.uitests, dumping entire logcat..."
+        Write-Warn "No logs found for com.microsoft.maui.uitests, dumping entire logcat..."
         & adb -s $DeviceUdid logcat -d > $deviceLogFile
     }
     
@@ -397,7 +397,7 @@ if (Test-Path $deviceLogFile) {
         Write-Host ""
         Write-Info "Full device log: $deviceLogFile"
     } else {
-        Write-Warning "Could not read device log file"
+        Write-Warn "Could not read device log file"
     }
     
     Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
diff --git a/.github/scripts/BuildAndRunSandbox.ps1 b/.github/scripts/BuildAndRunSandbox.ps1
index ccdffaafc082..c537f7c22af2 100644
--- a/.github/scripts/BuildAndRunSandbox.ps1
+++ b/.github/scripts/BuildAndRunSandbox.ps1
@@ -258,7 +258,7 @@ if ($Platform -eq "catalyst") {
             Write-Success "MacCatalyst Sandbox app launched with log capture"
         }
     } else {
-        Write-Warning "MacCatalyst Sandbox app not found at: $appPath"
+        Write-Warn "MacCatalyst Sandbox app not found at: $appPath"
     }
 }
 
@@ -379,7 +379,7 @@ try {
         # Fallback: If we couldn't get PID, dump entire logcat buffer (unfiltered)
         # This ensures we always have logs for the agent to analyze
         Write-Host ""
-        Write-Warning "Could not capture app PID from Appium test output"
+        Write-Warn "Could not capture app PID from Appium test output"
         Write-Info "Dumping entire logcat buffer (unfiltered)..."
         & adb -s $DeviceUdid logcat -d > $deviceLogFile
         Write-Info "Logcat dumped to: $deviceLogFile (UNFILTERED - contains all apps)"
@@ -469,7 +469,7 @@ try {
                 Write-Info "All logs are from Sandbox app only (Maui.Controls.Sample.Sandbox)"
             }
         } else {
-            Write-Warning "Could not read device log file"
+            Write-Warn "Could not read device log file"
         }
         
         Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
diff --git a/.github/scripts/Review-PR.ps1 b/.github/scripts/Review-PR.ps1
index 3df37e9216d2..1d8749d98aa6 100644
--- a/.github/scripts/Review-PR.ps1
+++ b/.github/scripts/Review-PR.ps1
@@ -83,11 +83,23 @@ param(
     [switch]$PostSummaryComment,
 
     [Parameter(Mandatory = $false)]
-    [switch]$RunFinalize
+    [switch]$RunFinalize,
+
+    [Parameter(Mandatory = $false)]
+    [string]$LogFile  # If provided, captures all output via Start-Transcript
 )
 
 $ErrorActionPreference = 'Stop'
 
+# Start transcript logging if LogFile specified (replaces external tee pipe)
+if ($LogFile) {
+    $logDir = Split-Path $LogFile -Parent
+    if ($logDir -and -not (Test-Path $logDir)) {
+        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
+    }
+    Start-Transcript -Path $LogFile -Force | Out-Null
+}
+
 # Get repository root
 $RepoRoot = git rev-parse --show-toplevel 2>$null
 if (-not $RepoRoot) {
@@ -298,7 +310,11 @@ if ($DryRun) {
         Write-Host "  2. pr-finalize skill (queued)" -ForegroundColor White
     }
     if ($PostSummaryComment) {
-        Write-Host "  3. ai-summary-comment skill (queued)" -ForegroundColor White
+        $phase3Label = "3. Post comments: agent summary"
+        if ($RunFinalize) {
+            $phase3Label += " + finalize"
+        }
+        Write-Host "  $phase3Label (queued)" -ForegroundColor White
     }
     Write-Host ""
     Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
@@ -351,6 +367,17 @@ if ($DryRun) {
     # Post-completion skills (only run if main agent completed successfully)
     if ($exitCode -eq 0) {
         
+        # Restore tracked files to clean state before running post-completion skills.
+        # Phase 1 (PR Agent) may have left the working tree dirty from try-fix attempts,
+        # which can cause skill files to be missing or modified in subsequent phases.
+        # NOTE: State files in CustomAgentLogsTmp/ are .gitignore'd and untracked,
+        # so this won't touch them. Using HEAD to also restore deleted files.
+        Write-Host ""
+        Write-Host "🧹 Restoring working tree to clean state between phases..." -ForegroundColor Yellow
+        git status --porcelain 2>$null | Set-Content "CustomAgentLogsTmp/PRState/phase1-exit-git-status.log" -ErrorAction SilentlyContinue
+        git checkout HEAD -- . 2>&1 | Out-Null
+        Write-Host "  ✅ Working tree restored" -ForegroundColor Green
+        
         # Phase 2: Run pr-finalize skill if requested
         if ($RunFinalize) {
             Write-Host ""
@@ -359,7 +386,13 @@ if ($DryRun) {
             Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
             Write-Host ""
             
-            $finalizePrompt = "Run the pr-finalize skill for PR #$PRNumber. Verify the PR title and description match the actual implementation. Do NOT post a comment - just update the state file at CustomAgentLogsTmp/PRState/pr-$PRNumber.md with your findings."
+            # Ensure output directory exists for finalize results
+            $finalizeDir = Join-Path $RepoRoot "CustomAgentLogsTmp/PRState/$PRNumber/pr-finalize"
+            if (-not (Test-Path $finalizeDir)) {
+                New-Item -ItemType Directory -Path $finalizeDir -Force | Out-Null
+            }
+            
+            $finalizePrompt = "Run the pr-finalize skill for PR #$PRNumber. Verify the PR title and description match the actual implementation. Do NOT post a comment. Write your findings to CustomAgentLogsTmp/PRState/$PRNumber/pr-finalize/pr-finalize-summary.md (NOT the main state file pr-$PRNumber.md which contains phase data that must not be overwritten). If you recommend a new description, also write it to CustomAgentLogsTmp/PRState/$PRNumber/pr-finalize/recommended-description.md. If you have code review findings, also write them to CustomAgentLogsTmp/PRState/$PRNumber/pr-finalize/code-review.md."
             
             $finalizeArgs = @(
                 "-p", $finalizePrompt,
@@ -378,30 +411,66 @@ if ($DryRun) {
             }
         }
         
-        # Phase 3: Run ai-summary-comment skill if requested (posts combined results)
+        # Phase 3: Post comments if requested
+        # Runs scripts directly instead of via Copilot CLI to avoid:
+        # - LLM creating its own broken version if skill files are missing
+        # - Dirty tree from Phase 2 corrupting script files
         if ($PostSummaryComment) {
             Write-Host ""
             Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
-            Write-Host "║  PHASE 3: POST SUMMARY COMMENT                            ║" -ForegroundColor Magenta
+            Write-Host "║  PHASE 3: POST COMMENTS                                   ║" -ForegroundColor Magenta
             Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
             Write-Host ""
             
-            $commentPrompt = "Use the ai-summary-comment skill to post a comment on PR #$PRNumber based on the results from the PR agent review and pr-finalize phases in CustomAgentLogsTmp/PRState/pr-$PRNumber.md."
-            
-            $commentArgs = @(
-                "-p", $commentPrompt,
-                "--allow-all",
-                "--stream", "on"
-            )
-            
-            Write-Host "💬 Posting summary comment..." -ForegroundColor Yellow
-            & copilot @commentArgs
+            # Restore tracked files (including deleted ones) to clean state.
+            Write-Host "🧹 Restoring working tree to clean state..." -ForegroundColor Yellow
+            git status --porcelain 2>$null | Set-Content "CustomAgentLogsTmp/PRState/phase2-exit-git-status.log" -ErrorAction SilentlyContinue
+            git checkout HEAD -- . 2>&1 | Out-Null
+            Write-Host "  ✅ Working tree restored" -ForegroundColor Green
             
-            $commentExit = $LASTEXITCODE
-            if ($commentExit -eq 0) {
-                Write-Host "✅ Summary comment posted" -ForegroundColor Green
+            # 3a: Post PR agent summary comment (from Phase 1 state file)
+            $scriptPath = ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1"
+            if (-not (Test-Path $scriptPath)) {
+                Write-Host "⚠️ Script missing after checkout, attempting targeted recovery..." -ForegroundColor Yellow
+                git checkout HEAD -- $scriptPath 2>&1 | Out-Null
+            }
+            if (Test-Path $scriptPath) {
+                Write-Host "💬 Running post-ai-summary-comment.ps1 directly..." -ForegroundColor Yellow
+                & $scriptPath -PRNumber $PRNumber
+                
+                $commentExit = $LASTEXITCODE
+                if ($commentExit -eq 0) {
+                    Write-Host "✅ Agent summary comment posted" -ForegroundColor Green
+                } else {
+                    Write-Host "⚠️ post-ai-summary-comment.ps1 exited with code: $commentExit" -ForegroundColor Yellow
+                }
             } else {
-                Write-Host "⚠️ ai-summary-comment exited with code: $commentExit" -ForegroundColor Yellow
+                Write-Host "⚠️ Script not found at: $scriptPath" -ForegroundColor Yellow
+                Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Gray
+                Write-Host "   Skipping agent summary comment." -ForegroundColor Gray
+            }
+            
+            # 3b: Post PR finalize comment (from Phase 2 finalize results)
+            if ($RunFinalize) {
+                $finalizeScriptPath = ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1"
+                if (-not (Test-Path $finalizeScriptPath)) {
+                    Write-Host "⚠️ Finalize script missing, attempting targeted recovery..." -ForegroundColor Yellow
+                    git checkout HEAD -- $finalizeScriptPath 2>&1 | Out-Null
+                }
+                if (Test-Path $finalizeScriptPath) {
+                    Write-Host "💬 Running post-pr-finalize-comment.ps1 directly..." -ForegroundColor Yellow
+                    & $finalizeScriptPath -PRNumber $PRNumber
+                    
+                    $finalizeCommentExit = $LASTEXITCODE
+                    if ($finalizeCommentExit -eq 0) {
+                        Write-Host "✅ Finalize comment posted" -ForegroundColor Green
+                    } else {
+                        Write-Host "⚠️ post-pr-finalize-comment.ps1 exited with code: $finalizeCommentExit" -ForegroundColor Yellow
+                    }
+                } else {
+                    Write-Host "⚠️ Script not found at: $finalizeScriptPath" -ForegroundColor Yellow
+                    Write-Host "   Skipping finalize comment." -ForegroundColor Gray
+                }
             }
         }
     }
@@ -417,3 +486,36 @@ if (-not $DryRun) {
     }
 }
 Write-Host ""
+
+# NOTE: This cleanup targets CI/ADO agent environments where only this script's
+# Copilot CLI processes should exist. On developer machines, this could potentially
+# affect other Copilot processes (e.g., VS Code extension). The risk is low since
+# this runs at script end, but be aware if running locally.
+# Clean up orphaned copilot CLI processes that may hold stdout fd open
+# IMPORTANT: Only target processes whose command line contains "copilot" to avoid
+# accidentally terminating the ADO agent's own node process
+Write-Host "🧹 Cleaning up child processes..." -ForegroundColor Gray
+try {
+    $myPid = $PID
+    # Find node processes running copilot CLI (not the ADO agent's node process)
+    $orphans = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
+        $_.Id -ne $myPid -and
+        (($_.Path -and $_.Path -match "copilot") -or
+         ($_.CommandLine -and $_.CommandLine -match "copilot"))
+    }
+    # Also get any process literally named "copilot"
+    $copilotProcs = Get-Process -Name "copilot" -ErrorAction SilentlyContinue
+    $allOrphans = @($orphans) + @($copilotProcs) | Where-Object { $_ -ne $null } | Sort-Object Id -Unique
+    if ($allOrphans.Count -gt 0) {
+        Write-Host "  Stopping $($allOrphans.Count) orphaned process(es): $($allOrphans | ForEach-Object { "$($_.ProcessName)($($_.Id))" } | Join-String -Separator ', ')" -ForegroundColor Gray
+        $allOrphans | Stop-Process -Force -ErrorAction SilentlyContinue
+    } else {
+        Write-Host "  No orphaned copilot processes found" -ForegroundColor Gray
+    }
+} catch {
+    Write-Host "  ⚠️ Cleanup warning: $_" -ForegroundColor Yellow
+}
+
+if ($LogFile) {
+    Stop-Transcript | Out-Null
+}
diff --git a/.github/scripts/shared/Build-AndDeploy.ps1 b/.github/scripts/shared/Build-AndDeploy.ps1
index 7a4b9172fe73..8abdafe7b21c 100644
--- a/.github/scripts/shared/Build-AndDeploy.ps1
+++ b/.github/scripts/shared/Build-AndDeploy.ps1
@@ -106,7 +106,13 @@ if ($Platform -eq "android") {
     
     Write-Step "Building $projectName for iOS..."
     
-    $buildArgs = @($ProjectPath, "-f", $TargetFramework, "-c", $Configuration)
+    # Detect host architecture for simulator builds
+    $hostArch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLower()
+    $runtimeId = if ($hostArch -eq "x64") { "iossimulator-x64" } else { "iossimulator-arm64" }
+    $simArch = if ($hostArch -eq "x64") { "x64" } else { "arm64" }
+    Write-Info "Host architecture: $hostArch, RuntimeIdentifier: $runtimeId"
+    
+    $buildArgs = @($ProjectPath, "-f", $TargetFramework, "-c", $Configuration, "-r", $runtimeId)
     if ($Rebuild) {
         $buildArgs += "--no-incremental"
     }
@@ -169,14 +175,27 @@ if ($Platform -eq "android") {
     }
     
     Write-Info "Searching for app bundle in: $artifactsDir"
+    
     $appPath = Get-ChildItem -Path $artifactsDir -Filter "*.app" -Recurse -ErrorAction SilentlyContinue | 
         Where-Object { 
-            $_.FullName -match "$Configuration.*iossimulator.*$projectName" -and 
+            $_.FullName -match "$Configuration.*iossimulator-$simArch.*$projectName" -and 
             $_.FullName -notmatch "\\obj\\" -and 
             $_.FullName -notmatch "/obj/"
         } |
         Select-Object -First 1
     
+    # Fallback: try any iossimulator build if specific arch not found
+    if (-not $appPath) {
+        Write-Info "Specific arch ($simArch) not found, trying any iossimulator build..."
+        $appPath = Get-ChildItem -Path $artifactsDir -Filter "*.app" -Recurse -ErrorAction SilentlyContinue | 
+            Where-Object { 
+                $_.FullName -match "$Configuration.*iossimulator.*$projectName" -and 
+                $_.FullName -notmatch "\\obj\\" -and 
+                $_.FullName -notmatch "/obj/"
+            } |
+            Select-Object -First 1
+    }
+    
     if (-not $appPath) {
         Write-Error "Could not find built app bundle in artifacts directory"
         Write-Info "Searched in: $artifactsDir"
diff --git a/.github/scripts/shared/Start-Emulator.ps1 b/.github/scripts/shared/Start-Emulator.ps1
index a0b57f3fc8b3..9fd9d227331a 100644
--- a/.github/scripts/shared/Start-Emulator.ps1
+++ b/.github/scripts/shared/Start-Emulator.ps1
@@ -50,11 +50,22 @@ if ($Platform -eq "android") {
         exit 1
     }
     
-    # Get device UDID if not provided OR if it's an AVD name that needs to be booted
+    # Get Android SDK path
+    $androidSdkRoot = $env:ANDROID_SDK_ROOT
+    if (-not $androidSdkRoot) {
+        $androidSdkRoot = $env:ANDROID_HOME
+    }
+    if (-not $androidSdkRoot) {
+        $androidSdkRoot = "$env:HOME/Library/Android/sdk"
+    }
+    
+    # Track which AVD to boot (may be set from DeviceUdid parameter if it's an AVD name)
+    $selectedAvd = $null
+    
     # Check if DeviceUdid is an AVD name (not an emulator-XXXX format)
     if ($DeviceUdid -and $DeviceUdid -notmatch "^emulator-\d+$") {
         # DeviceUdid is likely an AVD name - check if it's in the AVD list
-        $avdList = emulator -list-avds
+        $avdList = emulator -list-avds 2>$null
         if ($avdList -contains $DeviceUdid) {
             Write-Info "DeviceUdid '$DeviceUdid' is an AVD name. Will boot this emulator..."
             $selectedAvd = $DeviceUdid
@@ -70,11 +81,15 @@ if ($Platform -eq "android") {
         Write-Info "Auto-detecting Android device..."
         
         # Check for running devices first
-        $runningDevices = adb devices | Select-String "device$"
+        # Note: adb devices output can be:
+        #   emulator-5554	device    (basic)
+        #   emulator-5554          device product:... model:...    (with -l flag or some environments)
+        # We match any line starting with emulator- and containing "device" as the state
+        $runningDevices = adb devices | Select-String "^emulator-\d+\s+device"
         
         if ($runningDevices.Count -gt 0) {
-            # Use first running device
-            $DeviceUdid = ($runningDevices[0] -split '\s+')[0]
+            # Use first running device - extract just the emulator-XXXX part
+            $DeviceUdid = ($runningDevices[0].Line -split '\s+')[0]
             Write-Success "Found running Android device: $DeviceUdid"
         }
         else {
@@ -86,146 +101,226 @@ if ($Platform -eq "android") {
                 exit 1
             }
             
-            # Get list of available AVDs
-            $avdList = emulator -list-avds
-            
-            if (-not $avdList -or $avdList.Count -eq 0) {
-                Write-Error "No Android emulators found. Please create an Android Virtual Device (AVD) using Android Studio."
-                Write-Info "To create an AVD:"
-                Write-Info "  1. Open Android Studio"
-                Write-Info "  2. Go to Tools > Device Manager"
-                Write-Info "  3. Click 'Create Device' and follow the wizard"
-                exit 1
-            }
-            
-            Write-Info "Available emulators: $($avdList -join ', ')"
-            
-            # Selection priority:
-            # 1. API 30 Nexus device
-            # 2. Any API 30 device
-            # 3. Any Nexus device
-            # 4. First available device
-            
-            # $selectedAvd may already be set if AVD name was provided
-            # Only run auto-selection if not already set
+            # Get list of available AVDs (if not already set from parameter)
             if (-not $selectedAvd) {
+                $avdList = emulator -list-avds 2>$null
+                
+                if (-not $avdList -or $avdList.Count -eq 0) {
+                    Write-Error "No Android emulators found. Please create an Android Virtual Device (AVD) using Android Studio."
+                    Write-Info "To create an AVD:"
+                    Write-Info "  1. Open Android Studio"
+                    Write-Info "  2. Go to Tools > Device Manager"
+                    Write-Info "  3. Click 'Create Device' and follow the wizard"
+                    exit 1
+                }
+                
+                Write-Info "Available emulators: $($avdList -join ', ')"
+                
+                # Selection priority:
+                # 1. API 34 device (matches CI provisioning)
+                # 2. API 30 Nexus device
+                # 3. Any API 30 device
+                # 4. Any Nexus device
+                # 5. First available device
+                
+                # Try to find API 34 device (CI default)
+                $api34Device = $avdList | Where-Object { $_ -match "34|API.*34" } | Select-Object -First 1
+                if ($api34Device) {
+                    $selectedAvd = $api34Device
+                    Write-Info "Selected API 34 device: $selectedAvd"
+                }
+                
                 # Try to find API 30 Nexus device
-                $api30Nexus = $avdList | Where-Object { $_ -match "API.*30" -and $_ -match "Nexus" } | Select-Object -First 1
-                if ($api30Nexus) {
-                    $selectedAvd = $api30Nexus
-                    Write-Info "Selected API 30 Nexus device: $selectedAvd"
+                if (-not $selectedAvd) {
+                    $api30Nexus = $avdList | Where-Object { $_ -match "API.*30" -and $_ -match "Nexus" } | Select-Object -First 1
+                    if ($api30Nexus) {
+                        $selectedAvd = $api30Nexus
+                        Write-Info "Selected API 30 Nexus device: $selectedAvd"
+                    }
                 }
-            }
-            
-            # Try to find any API 30 device
-            if (-not $selectedAvd) {
-                $api30Device = $avdList | Where-Object { $_ -match "API.*30" } | Select-Object -First 1
-                if ($api30Device) {
-                    $selectedAvd = $api30Device
-                    Write-Info "Selected API 30 device: $selectedAvd"
+                
+                # Try to find any API 30 device
+                if (-not $selectedAvd) {
+                    $api30Device = $avdList | Where-Object { $_ -match "API.*30" } | Select-Object -First 1
+                    if ($api30Device) {
+                        $selectedAvd = $api30Device
+                        Write-Info "Selected API 30 device: $selectedAvd"
+                    }
+                }
+                
+                # Try to find any Nexus device
+                if (-not $selectedAvd) {
+                    $nexusDevice = $avdList | Where-Object { $_ -match "Nexus" } | Select-Object -First 1
+                    if ($nexusDevice) {
+                        $selectedAvd = $nexusDevice
+                        Write-Info "Selected Nexus device: $selectedAvd"
+                    }
+                }
+                
+                # Fall back to first available device
+                if (-not $selectedAvd) {
+                    $selectedAvd = $avdList[0]
+                    Write-Info "Selected first available device: $selectedAvd"
                 }
             }
             
-            # Try to find any Nexus device
-            if (-not $selectedAvd) {
-                $nexusDevice = $avdList | Where-Object { $_ -match "Nexus" } | Select-Object -First 1
-                if ($nexusDevice) {
-                    $selectedAvd = $nexusDevice
-                    Write-Info "Selected Nexus device: $selectedAvd"
-                }
+            # Start emulator with selected AVD
+            $emulatorBin = Join-Path $androidSdkRoot "emulator/emulator"
+            if ($IsWindows) {
+                $emulatorBin = "$emulatorBin.exe"
             }
             
-            # Fall back to first available device
-            if (-not $selectedAvd) {
-                $selectedAvd = $avdList[0]
-                Write-Info "Selected first available device: $selectedAvd"
+            # Check emulator binary exists
+            if (-not (Test-Path $emulatorBin)) {
+                # Fallback: try to find emulator on PATH
+                $emulatorCmd = Get-Command emulator -ErrorAction SilentlyContinue
+                if ($emulatorCmd) {
+                    $emulatorBin = $emulatorCmd.Source
+                    Write-Info "Using emulator from PATH: $emulatorBin"
+                } else {
+                    Write-Error "Emulator binary not found at: $emulatorBin"
+                    Write-Info "Looking for emulator in SDK..."
+                    Get-ChildItem -Path $androidSdkRoot -Filter "emulator*" -Recurse -Depth 2 -ErrorAction SilentlyContinue | ForEach-Object { Write-Info "  Found: $($_.FullName)" }
+                    exit 1
+                }
             }
             
             Write-Info "Starting emulator: $selectedAvd"
             Write-Info "This may take 1-2 minutes..."
             
-            # CRITICAL: Must use correct startup pattern for emulator to work
-            # On macOS/Linux, need to cd to emulator directory and use subshell
+            # Use swiftshader for software rendering (more reliable on CI without GPU)
+            # Redirect output to a log file for debugging
+            $emulatorLog = Join-Path ([System.IO.Path]::GetTempPath()) "emulator-$selectedAvd.log"
+            
             if ($IsWindows) {
-                Start-Process "emulator" -ArgumentList "-avd", $selectedAvd, "-no-snapshot-load", "-no-boot-anim" -WindowStyle Hidden
+                Start-Process $emulatorBin -ArgumentList "-avd", $selectedAvd, "-no-snapshot-load", "-no-boot-anim", "-gpu", "swiftshader_indirect" -WindowStyle Hidden
             }
             else {
-                # macOS/Linux: Use bash subshell pattern from platform-workflows.md
-                # This ensures emulator binary can find its dependencies
-                $androidHome = $env:ANDROID_HOME
-                if (-not $androidHome) {
-                    $androidHome = "$env:HOME/Library/Android/sdk"
-                }
-                
-                $emulatorDir = Join-Path $androidHome "emulator"
-                $emulatorBin = Join-Path $emulatorDir "emulator"
-                
-                if (-not (Test-Path $emulatorBin)) {
-                    Write-Error "Emulator binary not found at: $emulatorBin"
-                    Write-Info "Please ensure ANDROID_HOME is set correctly or Android SDK is installed."
-                    exit 1
-                }
-                
-                # Start emulator using bash subshell pattern (works correctly on macOS)
-                $startScript = "cd '$emulatorDir' && (./emulator -avd '$selectedAvd' -no-snapshot-load -no-audio -no-boot-anim > /tmp/emulator.log 2>&1 &)"
+                # macOS/Linux: Use nohup to detach from terminal
+                # Use -no-snapshot (not -no-snapshot-load) to ensure clean emulator state for CI/testing.
+                # This disables both snapshot load and save, so each boot is a cold boot.
+                # Trade-off: slower boots, but guarantees no stale state between test runs.
+                $startScript = "nohup '$emulatorBin' -avd '$selectedAvd' -no-window -no-snapshot -no-audio -no-boot-anim -gpu swiftshader_indirect > '$emulatorLog' 2>&1 &"
                 bash -c $startScript
-                
-                Write-Info "Emulator started in background. Log file: /tmp/emulator.log"
+                Write-Info "Emulator started in background. Log file: $emulatorLog"
             }
             
-            # Wait for emulator to appear in adb devices
-            Write-Info "Waiting for emulator to start..."
-            $timeout = 120
-            $elapsed = 0
-            $emulatorStarted = $false
+            # Give the emulator process time to start
+            Start-Sleep -Seconds 5
             
-            while ($elapsed -lt $timeout) {
-                Start-Sleep -Seconds 2
-                $elapsed += 2
-                
-                $devices = adb devices | Select-String "emulator.*device$"
+            # Check if emulator process is running
+            if ($IsWindows) {
+                $emulatorProcs = (Get-Process -Name "emulator*","qemu*" -ErrorAction SilentlyContinue | 
+                    Where-Object { $_.CommandLine -match [regex]::Escape($selectedAvd) }).Id -join "`n"
+            } else {
+                $emulatorProcs = bash -c "pgrep -f 'qemu.*$selectedAvd' || pgrep -f 'emulator.*$selectedAvd' || true" 2>&1
+            }
+            if ([string]::IsNullOrWhiteSpace($emulatorProcs)) {
+                Write-Error "Emulator process did not start. Checking log..."
+                if (Test-Path $emulatorLog) {
+                    Get-Content $emulatorLog | Select-Object -Last 50 | ForEach-Object { Write-Info "  $_" }
+                }
+                exit 1
+            }
+            Write-Info "Emulator process started (PIDs: $emulatorProcs)"
+            
+            # Wait for device to appear with timeout
+            # Timeout of 120s (2 min) - if the emulator hasn't registered an ADB device by then, it's not going to
+            Write-Info "Waiting for emulator device to appear..."
+            $deviceTimeout = 120
+            $deviceWaited = 0
+            
+            while ($deviceWaited -lt $deviceTimeout) {
+                # Match any emulator device line
+                $devices = adb devices | Select-String "^emulator-\d+\s+device"
                 if ($devices.Count -gt 0) {
-                    $DeviceUdid = ($devices[0] -split '\s+')[0]
-                    $emulatorStarted = $true
+                    $DeviceUdid = ($devices[0].Line -split '\s+')[0]
                     Write-Info "Emulator detected: $DeviceUdid"
                     break
                 }
                 
-                if ($elapsed % 10 -eq 0) {
-                    Write-Info "Still waiting... ($elapsed seconds elapsed)"
+                # Check for offline state
+                $offlineDevices = adb devices | Select-String "^emulator-\d+\s+offline"
+                if ($offlineDevices.Count -gt 0) {
+                    Write-Info "Device found but offline, waiting..."
+                }
+                
+                Start-Sleep -Seconds 5
+                $deviceWaited += 5
+                
+                if ($deviceWaited % 30 -eq 0) {
+                    Write-Info "Still waiting... ($deviceWaited seconds elapsed)"
+                    # Show emulator log tail if taking too long
+                    if ((Test-Path $emulatorLog)) {
+                        Write-Info "Emulator log (last 5 lines):"
+                        Get-Content $emulatorLog | Select-Object -Last 5 | ForEach-Object { Write-Info "  $_" }
+                    }
                 }
             }
             
-            if (-not $emulatorStarted) {
-                Write-Error "Emulator failed to start within $timeout seconds. Please try starting it manually."
+            if (-not $DeviceUdid) {
+                Write-Error "Emulator failed to start within $deviceTimeout seconds. Please try starting it manually."
+                Write-Info "Current adb devices:"
+                adb devices -l
+                if (Test-Path $emulatorLog) {
+                    Write-Info "Emulator log (last 30 lines):"
+                    Get-Content $emulatorLog | Select-Object -Last 30 | ForEach-Object { Write-Info "  $_" }
+                }
                 exit 1
             }
             
             # Wait for boot to complete
             Write-Info "Waiting for emulator to finish booting..."
-            $bootTimeout = 120
+            $bootTimeout = 600
             $bootElapsed = 0
-            $bootCompleted = $false
             
             while ($bootElapsed -lt $bootTimeout) {
-                Start-Sleep -Seconds 2
-                $bootElapsed += 2
-                
                 $bootStatus = adb -s $DeviceUdid shell getprop sys.boot_completed 2>$null
                 if ($bootStatus -match "1") {
-                    $bootCompleted = $true
                     Write-Success "Emulator fully booted: $DeviceUdid"
                     break
                 }
                 
-                if ($bootElapsed % 10 -eq 0) {
+                Start-Sleep -Seconds 5
+                $bootElapsed += 5
+                
+                if ($bootElapsed % 30 -eq 0) {
                     Write-Info "Still booting... ($bootElapsed seconds elapsed)"
                 }
             }
             
-            if (-not $bootCompleted) {
-                Write-Error "Emulator failed to complete boot within $bootTimeout seconds. It may still be starting."
+            if ($bootElapsed -ge $bootTimeout) {
+                Write-Error "Emulator failed to complete boot within $bootTimeout seconds."
                 Write-Info "You can check status with: adb -s $DeviceUdid shell getprop sys.boot_completed"
+                if (Test-Path $emulatorLog) {
+                    Write-Info "Emulator log (last 30 lines):"
+                    Get-Content $emulatorLog | Select-Object -Last 30 | ForEach-Object { Write-Info "  $_" }
+                }
+                exit 1
+            }
+            
+            # Wait for package manager service to be available (critical for app installation)
+            Write-Info "Waiting for package manager service..."
+            $pmTimeout = 120
+            $pmWaited = 0
+            
+            while ($pmWaited -lt $pmTimeout) {
+                $pmOutput = adb -s $DeviceUdid shell pm list packages 2>$null
+                if ($pmOutput -match "package:") {
+                    Write-Info "Package manager service is ready"
+                    break
+                }
+                Start-Sleep -Seconds 3
+                $pmWaited += 3
+                if ($pmWaited % 15 -eq 0) {
+                    Write-Info "Waiting for package manager... ($pmWaited seconds elapsed)"
+                }
+            }
+            
+            if ($pmWaited -ge $pmTimeout) {
+                Write-Error "Package manager service did not start within $pmTimeout seconds."
+                Write-Info "Checking services:"
+                adb -s $DeviceUdid shell service list 2>$null | Select-Object -First 20 | ForEach-Object { Write-Info "  $_" }
                 exit 1
             }
         }
@@ -249,29 +344,105 @@ if ($Platform -eq "android") {
         Write-Info "Auto-detecting iOS simulator..."
         $simList = xcrun simctl list devices available --json | ConvertFrom-Json
         
-        # Find iPhone Xs with iOS 18.5 (default for UI tests)
-        $iPhoneXs = $simList.devices.PSObject.Properties | 
-            Where-Object { $_.Name -match "iOS-18-5" } |
-            ForEach-Object { 
-                $_.Value | Where-Object { $_.name -eq "iPhone Xs" }
-            } | 
-            Select-Object -First 1
+        # Preferred devices in order of priority
+        $preferredDevices = @("iPhone 16 Pro", "iPhone 15 Pro", "iPhone 14 Pro", "iPhone Xs")
+        # Preferred iOS versions in order (stable preferred, beta fallback)
+        $preferredVersions = @("iOS-18", "iOS-17", "iOS-26")
+        
+        $selectedDevice = $null
+        $selectedVersion = $null
         
-        if (-not $iPhoneXs) {
-            Write-Error "No iPhone Xs simulator found with iOS 18.5. Please create one in Xcode."
-            Write-Info "Available iOS 18.5 simulators:"
-            $simList.devices.PSObject.Properties | 
-                Where-Object { $_.Name -match "iOS-18-5" } |
-                ForEach-Object { 
-                    $_.Value | ForEach-Object { Write-Info "  - $($_.name) ($($_.udid))" }
+        # Try each preferred version
+        foreach ($version in $preferredVersions) {
+            if ($selectedDevice) { break }
+            
+            # Get all runtimes matching this version prefix
+            $matchingRuntimes = $simList.devices.PSObject.Properties | 
+                Where-Object { $_.Name -match $version }
+            
+            if ($matchingRuntimes) {
+                # Try each preferred device
+                foreach ($deviceName in $preferredDevices) {
+                    $device = $null
+                    $deviceRuntime = $null
+                    foreach ($rt in $matchingRuntimes) {
+                        $found = $rt.Value | Where-Object { $_.name -eq $deviceName -and $_.isAvailable -eq $true } | Select-Object -First 1
+                        if ($found) {
+                            $device = $found
+                            $deviceRuntime = $rt.Name
+                            break
+                        }
+                    }
+                    
+                    if ($device) {
+                        $selectedDevice = $device
+                        $selectedVersion = $deviceRuntime
+                        Write-Info "Found preferred device: $deviceName on $selectedVersion"
+                        break
+                    }
+                }
+                
+                # If no preferred device found, take first available iPhone
+                if (-not $selectedDevice) {
+                    $anyiPhone = $null
+                    $iphoneRuntime = $null
+                    foreach ($rt in $matchingRuntimes) {
+                        $found = $rt.Value | Where-Object { $_.name -match "iPhone" -and $_.isAvailable -eq $true } | Select-Object -First 1
+                        if ($found) {
+                            $anyiPhone = $found
+                            $iphoneRuntime = $rt.Name
+                            break
+                        }
+                    }
+                    
+                    if ($anyiPhone) {
+                        $selectedDevice = $anyiPhone
+                        $selectedVersion = $iphoneRuntime
+                        Write-Info "Using available iPhone: $($anyiPhone.name) on $selectedVersion"
+                    }
                 }
+            }
+        }
+        
+        # Last resort: find ANY available iPhone simulator
+        if (-not $selectedDevice) {
+            $allDevices = $simList.devices.PSObject.Properties | ForEach-Object { 
+                $runtime = $_.Name
+                $_.Value | Where-Object { $_.name -match "iPhone" -and $_.isAvailable -eq $true } | 
+                    ForEach-Object { $_ | Add-Member -NotePropertyName "runtime" -NotePropertyValue $runtime -PassThru }
+            }
+            
+            if ($allDevices) {
+                $selectedDevice = $allDevices | Select-Object -First 1
+                $selectedVersion = $selectedDevice.runtime
+                Write-Info "Fallback: Using $($selectedDevice.name) on $selectedVersion"
+            }
+        }
+        
+        if (-not $selectedDevice) {
+            Write-Error "No iPhone simulator found. Please create one in Xcode."
+            Write-Info "Available simulators:"
+            $simList.devices.PSObject.Properties | ForEach-Object { 
+                $runtime = $_.Name
+                $_.Value | Where-Object { $_.isAvailable -eq $true } | ForEach-Object { 
+                    Write-Info "  - $($_.name) ($runtime) - $($_.udid)" 
+                }
+            }
             exit 1
         }
         
-        $DeviceUdid = $iPhoneXs.udid
+        $DeviceUdid = $selectedDevice.udid
     }
     
-    Write-Success "iOS simulator: $DeviceUdid (iOS 18.5)"
+    # Get device name for display
+    $simState = xcrun simctl list devices --json | ConvertFrom-Json
+    $deviceInfo = $simState.devices.PSObject.Properties.Value | 
+        ForEach-Object { $_ } | 
+        Where-Object { $_.udid -eq $DeviceUdid } | 
+        Select-Object -First 1
+    $deviceName = if ($deviceInfo) { $deviceInfo.name } else { "Unknown" }
+    
+    Write-Success "iOS simulator: $deviceName ($DeviceUdid)"
     
     # Boot simulator if not already booted
     Write-Info "Booting simulator (if not already running)..."
diff --git a/.github/scripts/shared/shared-utils.ps1 b/.github/scripts/shared/shared-utils.ps1
index fbdb6309cb2f..21477d0d09bb 100644
--- a/.github/scripts/shared/shared-utils.ps1
+++ b/.github/scripts/shared/shared-utils.ps1
@@ -24,6 +24,11 @@ function Write-Success {
     Write-Host "✅ $Message" -ForegroundColor Green
 }
 
+function Write-Warn {
+    param([string]$Message)
+    Write-Host "⚠️  $Message" -ForegroundColor Yellow
+}
+
 function Write-Error {
     param([string]$Message)
     Write-Host "❌ $Message" -ForegroundColor Red
diff --git a/.github/skills/try-fix/SKILL.md b/.github/skills/try-fix/SKILL.md
index 0e89f53ba9a7..291283981e3c 100644
--- a/.github/skills/try-fix/SKILL.md
+++ b/.github/skills/try-fix/SKILL.md
@@ -318,7 +318,7 @@ git diff | Set-Content "$OUTPUT_DIR/fix.diff"
 
 ```bash
 pwsh .github/scripts/EstablishBrokenBaseline.ps1 -Restore
-git checkout -- .
+git checkout HEAD -- .
 ```
 
 ### Step 9: Report Results
@@ -361,14 +361,11 @@ If `state_file` input was provided and file exists:
 |---|--------|----------|-------------|---------------|-------|
 | N | try-fix #N | [approach] | ✅ PASS / ❌ FAIL | [files] | [analysis] |
 
-4. **Commit state file:**
-```bash
-git add "$STATE_FILE" && git commit -m "try-fix: attempt #N"
-```
-
 **If no state file provided:** Skip this step (results returned to invoker only).
 
-**⚠️ IMPORTANT: Do NOT set any "Exhausted" field.** Cross-pollination exhaustion is determined by the pr agent after invoking ALL 5 models and confirming none have new ideas. try-fix only reports its own attempt result.
+**⚠️ Do NOT `git add` or `git commit` the state file.** It lives in `CustomAgentLogsTmp/` which is `.gitignore`d. Committing it with `git add -f` would cause `git checkout HEAD -- .` (used between phases) to revert it, losing data.
+
+**⚠️ IMPORTANT: Do NOT set any "Exhausted" field.** Cross-pollination exhaustion is determined by the pr agent after invoking ALL 6 models and confirming none have new ideas. try-fix only reports its own attempt result.
 
 **Ownership rule:** try-fix updates its own row ONLY. Never modify:
 - Phase status fields
@@ -383,7 +380,7 @@ git add "$STATE_FILE" && git commit -m "try-fix: attempt #N"
 | Test command fails to run | Report build/setup error with details |
 | Test times out | Report timeout, include partial output |
 | Can't determine fix approach | Report "no viable approach identified" with reasoning |
-| Git state unrecoverable | Run `git checkout -- .` and `git clean -fd` if needed |
+| Git state unrecoverable | Run `git checkout HEAD -- .` and `git clean -fd` if needed |
 
 ---
 
diff --git a/eng/devices/android.cake b/eng/devices/android.cake
index f17028459a3f..3038486adb99 100644
--- a/eng/devices/android.cake
+++ b/eng/devices/android.cake
@@ -5,7 +5,7 @@
 const int DefaultApiLevel = 30;
 
 const int EmulatorStartProcessTimeoutSeconds = 1 * 60;
-const int EmulatorBootTimeoutSeconds = 2 * 60;
+const int EmulatorBootTimeoutSeconds = 10 * 60;
 const int EmulatorKillTimeoutSeconds = 1 * 60;
 const int AdbCommandTimeoutSeconds = 30;
 


PATCH

echo "Patch applied successfully."
