# docs: refresh CLAUDE.md to match current codebase state

Source: [mm7894215/TokenTracker#8](https://github.com/mm7894215/TokenTracker/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Add Hermes Agent as 9th provider (SQLite sessions table)
- Update file line counts (rollout 3020, local-api 961, usage-limits 1151, init 912, sync 840)
- Document new dashboard pages: IpCheck, Widgets, Limits, Settings, LoginPage, LeaderboardProfile, NativeAuthCallback
- Document share card feature (Broadsheet + Neon annual-report variants + native-save bridge)
- Update copy.csv string count (~550) and test count (~95)
- Expand macOS app service/model layer (NativeBridge, APIClient, UpdateChecker, WidgetSnapshotWriter, TokenTrackerWidget)
- Note macOS 12 support and universal arm64+x64 build
- Clarify cloud backend lives in separate repo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
