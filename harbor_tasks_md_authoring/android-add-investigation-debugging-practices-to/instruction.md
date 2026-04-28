# Add investigation & debugging practices to copilot-instructions

Source: [dotnet/android#11141](https://github.com/dotnet/android/pull/11141)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Description

Adds an "Investigation & Debugging Practices" section to `.github/copilot-instructions.md` capturing five high-leverage lessons from the CoreCLRTrimmable CI lane investigation (#11091):

1. **Reproduce CI failures locally — do not iterate through CI.** Includes the exact `make` + `dotnet-local.sh` invocation for device tests.
2. **Nuke `bin/` and `obj/` when the build enters a weird state.** Stale incremental output causes phantom errors.
3. **Verify code paths with logging before reasoning about them.** Absence of log output is itself evidence.
4. **Decompile the produced `.dll` when generated code misbehaves.** Don't trust generator source to tell you what it emitted.
5. **`am instrument` going silent means it crashed, not hung.** Check `logcat` for the fatal signal.

These rules target failure modes that cost significant time during PR #11091 — each one would have caught a real dead-end before hours were spent on it.

Split out from #11091 to keep the tests/CI PR focused.

## Follow-up issues filed during the same retrospective

- #11136 — fail CI immediately when `am instrument` crashes
- #11137 — skill: reproduce CI runs locally
- #11138 — skill: trimmable-type-map troubleshooting
- #11139 — skill: diagnosing dotnet/android cross-language
- #11140 — generator output unit tests for trimmable typemap

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
