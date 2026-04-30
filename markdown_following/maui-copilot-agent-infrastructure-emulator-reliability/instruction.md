# Copilot Agent Infrastructure: Reliability and Consistency Improvements

## Context

This repository runs a Copilot-driven PR review workflow built from PowerShell
scripts under `.github/scripts/` and AI-agent instruction files under
`.github/agents/pr/` and `.github/skills/`. Several of these pieces are
unreliable in CI or have drifted out of sync with each other. The symptoms
below need to be addressed; the resulting code/docs must be internally
consistent.

## Symptoms to address

### 1. Inconsistent warning output

`shared-utils.ps1` defines a family of logging helpers — `Write-Step`,
`Write-Info`, `Write-Success`, and `Write-Error` — but no warning helper
following the same pattern. Various scripts fall back to PowerShell's built-in
`Write-Warning` cmdlet, which doesn't integrate with the rest of the logging
style. Provide a sibling helper named `Write-Warn` in `shared-utils.ps1`
matching the pattern of the existing helpers (callable as
`Write-Warn 'some message'` and emitting the message to output).

The warning call sites in `BuildAndRunHostApp.ps1` and `BuildAndRunSandbox.ps1`
should use the new helper. In particular, the warnings in
`BuildAndRunHostApp.ps1` covering:

- the MacCatalyst app being not found at the expected path (begins
  `"MacCatalyst app not found ...`),
- the device-log file being unreadable (begins `"Could not read device log ...`),
- the per-package logcat lookup turning up empty (begins
  `"No logs found for ...`)

must call the new helper rather than `Write-Warning`.

### 2. `Review-PR.ps1` log capture and dirty working tree between phases

`Review-PR.ps1` orchestrates multiple phases (the main PR agent, optional
finalize phase, optional comment-posting phase). Two related problems:

a. **Log capture.** The current external pipe approach for capturing the
   script's output is unreliable and can leave child processes hanging.
   Add a `[string]$LogFile` parameter; when it is supplied, the script must
   capture all of its output via `Start-Transcript` at startup and
   `Stop-Transcript` at the end.

b. **Working tree restoration between phases.** Earlier phases may modify
   tracked files (try-fix attempts, finalize edits). Subsequent phases assume
   a clean tree, and skill files becoming missing/modified causes ENOENT and
   parse errors. Before each subsequent phase begins, restore the tree to its
   committed state using `git checkout HEAD -- .`. This must happen at every
   phase boundary inside the orchestration (so the literal restoration command
   appears more than once in the script).

### 3. Android emulator boot timeout is too short

`eng/devices/android.cake` declares `EmulatorBootTimeoutSeconds` for how long
the build may wait for an emulator to finish booting. The current value is
too low — emulators in CI environments routinely exceed it and the run fails
spuriously. Set the timeout to ten minutes, expressed as `10 * 60` to remain
consistent with the surrounding constants in that file.

### 4. Stale model references in agent instruction files

The PR-agent instruction files `.github/agents/pr/PLAN-TEMPLATE.md` and
`.github/agents/pr/SHARED-RULES.md` reference a retired model name,
`claude-opus-4.5`. The currently supported model is `claude-opus-4.6`. After
the fix, the new name must appear in both files and the old name must not
appear in either.

### 5. `post-gate.md` lacks environment-blocker rules and cleanup guidance

`.github/agents/pr/post-gate.md` controls the Phase 3/4 try-fix workflow and
is missing two pieces of guidance that lead to broken runs:

a. **Stop on environment blockers (Phase 4).** When try-fix cannot run
   because the host environment is missing prerequisites, the agent should
   stop and ask the user instead of marking attempts blocked and continuing.
   Add a section titled exactly **"Stop on Environment Blockers"** that
   enumerates the blocker conditions; the list must include
   **"Missing Appium drivers"** and **"Device/emulator not available"**
   (other plausible blockers are fine to add as well).

b. **Mandatory cleanup between try-fix attempts.** Each try-fix attempt may
   modify tracked files and add untracked files; if the next attempt starts
   from a dirty tree, skill files become corrupted and results are
   misleading. The document must require running, between each pair of
   attempts:

   - `git checkout HEAD -- .` — restore tracked files (including those an
     attempt deleted) to the merged PR state, and
   - `git clean -fd` — remove untracked files added by the previous attempt.

   The cleanup must explicitly preserve the directory `CustomAgentLogsTmp/`
   (it holds gitignored, cross-attempt state that subsequent phases need to
   read). Mention this exclusion in the document.

### 6. `try-fix` SKILL.md should warn against committing state files

`.github/skills/try-fix/SKILL.md` describes how the skill writes a per-attempt
state file. The state file lives under `CustomAgentLogsTmp/`, which is
`.gitignore`d. If an author tries to `git add` (or `git add -f`) and commit
that state file, the cleanup step from item 5 above (`git checkout HEAD -- .`,
which runs between phases) will revert it and silently lose the data.

`SKILL.md` must contain a warning that mentions `git add` in connection with
state files and explains that the state directory is gitignored — either by
naming `CustomAgentLogsTmp` directly or by referring to the file as
`gitignored`. The warning's intent is to tell readers not to commit state
files.

## Files involved

The following files are the ones that need changes to address the symptoms
above. Localize and edit only what's necessary; do not restructure these
files beyond the symptoms described.

- `.github/scripts/shared/shared-utils.ps1`
- `.github/scripts/BuildAndRunHostApp.ps1`
- `.github/scripts/BuildAndRunSandbox.ps1`
- `.github/scripts/Review-PR.ps1`
- `eng/devices/android.cake`
- `.github/agents/pr/PLAN-TEMPLATE.md`
- `.github/agents/pr/SHARED-RULES.md`
- `.github/agents/pr/post-gate.md`
- `.github/skills/try-fix/SKILL.md`

## Notes

- The agent instruction files (`PLAN-TEMPLATE.md`, `SHARED-RULES.md`,
  `post-gate.md`, `SKILL.md`) describe how AI agents interact with this
  repository, so they must stay consistent with the actual script behavior.
- All PowerShell scripts in this repo must remain parseable and must not
  introduce syntax errors; the existing helper exports from
  `shared-utils.ps1` (`Write-Step`, `Write-Info`, `Write-Success`,
  `Write-Error`) must continue to be available.
