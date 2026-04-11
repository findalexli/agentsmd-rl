# Copilot Agent Infrastructure: Script Hardening and Instruction Updates

## Problem

Several issues affect the reliability of the Copilot agent infrastructure scripts in this repository:

1. **`Write-Warning` inconsistency**: The scripts in `.github/scripts/` use `Write-Warning` for log output, but this is a built-in PowerShell cmdlet that doesn't integrate with the custom logging system in `shared-utils.ps1`. The scripts need a consistent `Write-Warn` helper that follows the same pattern as `Write-Success`, `Write-Error`, and `Write-Info`.

2. **Review-PR.ps1 hangs on log capture**: The `Review-PR.ps1` script uses an external `tee` pipe for log capture, which can cause process hangs. It also doesn't restore the working tree between phases, leading to dirty state when skills modify files.

3. **Android emulator boot timeout is too short**: The emulator boot timeout in `eng/devices/android.cake` is set to 2 minutes, which is insufficient for CI environments. Emulators routinely take longer than 2 minutes to fully boot.

4. **Outdated model references**: The agent instruction files (`PLAN-TEMPLATE.md`, `SHARED-RULES.md`) reference an older AI model version (`claude-opus-4.5`) that has been superseded.

5. **Missing try-fix cleanup rules**: The agent instruction files don't specify mandatory cleanup steps between try-fix attempts, leading to dirty working trees that cause skill file corruption and ENOENT errors. There are also no environment blocker stop rules in the post-gate phases.

## Files to Look At

- `.github/scripts/shared/shared-utils.ps1` — shared logging helpers, needs `Write-Warn`
- `.github/scripts/BuildAndRunHostApp.ps1` — uses `Write-Warning`, should use `Write-Warn`
- `.github/scripts/BuildAndRunSandbox.ps1` — same `Write-Warning` issue
- `.github/scripts/Review-PR.ps1` — needs `-LogFile` parameter with `Start-Transcript`, and working tree restoration between phases
- `.github/scripts/shared/Start-Emulator.ps1` — Android SDK discovery and boot reliability
- `.github/scripts/shared/Build-AndDeploy.ps1` — iOS simulator architecture detection
- `eng/devices/android.cake` — emulator boot timeout configuration
- `.github/agents/pr/PLAN-TEMPLATE.md` — model references need updating
- `.github/agents/pr/SHARED-RULES.md` — model table needs updating
- `.github/agents/pr/post-gate.md` — needs environment blocker rules and mandatory cleanup steps between try-fix attempts
- `.github/skills/try-fix/SKILL.md` — needs warning about not committing state files

## Notes

- After fixing the code, update the relevant agent instruction files to reflect the changes.
- The instruction files define how AI agents interact with this repository, so they must stay consistent with the actual script behavior.
- The `SHARED-RULES.md` and `PLAN-TEMPLATE.md` model table should reflect the current set of AI models used for try-fix exploration.
- The `post-gate.md` file controls Phase 3-4 agent behavior and needs explicit rules about stopping on environment blockers and cleaning up between attempts.
