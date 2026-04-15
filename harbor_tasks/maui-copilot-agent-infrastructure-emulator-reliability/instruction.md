# Copilot Agent Infrastructure: Script Hardening and Instruction Updates

## Problem

Several issues affect the reliability of the Copilot agent infrastructure scripts in this repository:

1. **`Write-Warning` inconsistency**: The scripts in `.github/scripts/` use `Write-Warning` for log output, but this is a built-in PowerShell cmdlet that doesn't integrate with the custom logging system in `shared-utils.ps1`. The scripts need a consistent warning helper that follows the same pattern as `Write-Success`, `Write-Error`, and `Write-Info`.

2. **Review-PR.ps1 log capture issues**: The `Review-PR.ps1` script uses an external pipe mechanism for log capture, which can cause process hangs. It also doesn't restore the working tree between phases, leading to dirty state when skills modify files.

3. **Android emulator boot timeout is too short**: The emulator boot timeout in `eng/devices/android.cake` is set to 2 minutes, which is insufficient for CI environments. Emulators routinely take longer than 2 minutes to fully boot. The timeout should be increased to at least 10 minutes.

4. **Outdated model references**: The agent instruction files (`PLAN-TEMPLATE.md`, `SHARED-RULES.md`) reference an older AI model version (`claude-opus-4.5`) that has been superseded by `claude-opus-4.6`.

5. **Missing try-fix cleanup rules**: The agent instruction files don't specify mandatory cleanup steps between try-fix attempts, leading to dirty working trees that cause skill file corruption and ENOENT errors. There are also no environment blocker stop rules in the post-gate phases. Specifically, `post-gate.md` must document:
   - Running `git checkout HEAD -- .` to restore tracked files between attempts
   - Running `git clean -fd --exclude=CustomAgentLogsTmp/` to remove untracked files
   - That `CustomAgentLogsTmp/` must be excluded from cleanup
   - Stop rules for Phase 4 when environment blockers are encountered (Missing Appium drivers, device/emulator not available)

6. **try-fix SKILL.md state file warning**: The try-fix skill should warn against using `git add` or `git commit` for state files in `CustomAgentLogsTmp/` because that directory is `.gitignore`d and committing state would cause `git checkout HEAD -- .` (used between phases) to revert the state file, losing data.

## Files to Look At

- `.github/scripts/shared/shared-utils.ps1` — shared logging helpers, needs a warning helper function
- `.github/scripts/BuildAndRunHostApp.ps1` — uses `Write-Warning`, should use the consistent warning helper
- `.github/scripts/BuildAndRunSandbox.ps1` — same warning helper issue
- `.github/scripts/Review-PR.ps1` — needs working tree restoration between phases
- `.github/scripts/shared/Start-Emulator.ps1` — Android SDK discovery and boot reliability
- `.github/scripts/shared/Build-AndDeploy.ps1` — iOS simulator architecture detection
- `eng/devices/android.cake` — emulator boot timeout configuration, currently 2 minutes, needs to be increased to 10 minutes
- `.github/agents/pr/PLAN-TEMPLATE.md` — model references need updating from `claude-opus-4.5` to `claude-opus-4.6`
- `.github/agents/pr/SHARED-RULES.md` — model table needs updating from `claude-opus-4.5` to `claude-opus-4.6`
- `.github/agents/pr/post-gate.md` — needs environment blocker rules (Missing Appium drivers, Device/emulator not available) and mandatory cleanup steps between try-fix attempts (`git checkout HEAD -- .`, `git clean -fd --exclude=CustomAgentLogsTmp/`, excluding `CustomAgentLogsTmp/` from cleanup)
- `.github/skills/try-fix/SKILL.md` — needs warning about not committing state files (since `CustomAgentLogsTmp/` is gitignored, using `git add` would cause state loss when `git checkout HEAD -- .` is run between phases)

## Notes

- After fixing the code, update the relevant agent instruction files to reflect the changes.
- The instruction files define how AI agents interact with this repository, so they must stay consistent with the actual script behavior.
- The `SHARED-RULES.md` and `PLAN-TEMPLATE.md` model table should reflect the current set of AI models used for try-fix exploration. The model `claude-opus-4.5` should be replaced with `claude-opus-4.6`.
- The `post-gate.md` file controls Phase 3-4 agent behavior and needs explicit rules about stopping on environment blockers and cleaning up between attempts.
- The `post-gate.md` Cross-Pollination table references should reflect 6 models, not 5.
