# Improve try-fix skill: standardize outputs, add execution constraints, and fix preview comment handling

## Problem

The `try-fix` skill (`.github/skills/try-fix/SKILL.md`) has several issues that need to be addressed:

1. **Inconsistent result values**: The skill documents result values as `PASS` or `FAIL`, but the codebase uses title-case `Pass`/`Fail` elsewhere. There's also no way to report when a device/emulator is unavailable — the skill forces agents to report either pass or fail even when testing is blocked.

2. **Missing execution constraints**: The skill doesn't warn that try-fix runs must execute sequentially. When multiple agents run try-fix in parallel, they overwrite each other's source changes and corrupt device test results.

3. **Duplicated output structure**: The output structure documentation lives in a separate `references/output-structure.md` file, duplicating content already in `SKILL.md`. The SKILL.md itself references this file instead of containing the information inline.

4. **Missing log capture**: The workflow steps for running baseline and test scripts don't capture their output to log files, making it impossible to verify that baseline was established or to debug test failures.

5. **Missing compatibility metadata**: The skill frontmatter lacks a `compatibility` field to document runtime requirements.

6. **Preview comment bug**: The PowerShell script at `.github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1` has a bug in its preview file handling: when updating an existing preview file that already has a TRY-FIX section, it replaces the *entire* section instead of preserving previous attempts. The GitHub comment path already handles this correctly (extracting existing content and appending), but the preview/dry-run path does not.

## Expected Behavior

- SKILL.md should use consistent result values (`Pass`, `Fail`, `Blocked`) and document when each applies
- SKILL.md should warn about sequential execution requirements
- The output structure reference file should be removed and its content incorporated into SKILL.md
- Workflow code examples should capture output using `Tee-Object` for log files
- The PS1 script's preview path should preserve previous attempts when updating (matching the GitHub comment path's behavior)

## Files to Look At

- `.github/skills/try-fix/SKILL.md` — the skill definition that needs documentation updates
- `.github/skills/try-fix/references/output-structure.md` — duplicated content to be removed
- `.github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1` — PowerShell script with the preview comment handling bug (look at the `$DryRun` code path around line 410)

After making the code fix to the PowerShell script, update the try-fix skill documentation to reflect the improvements. The skill file should be a complete, self-contained reference without depending on auxiliary files for core information.
