# Fix buildable-folder header visibility and generation crash

## Problem

When a Tuist target uses **buildable folders** (synchronized groups) and declares Objective-C headers in the target's `headers` property, project generation can crash or silently lose header visibility.

The crash happens because `BuildPhaseGenerator.generateHeadersBuildPhase` tries to look up file references for headers that live inside a synchronized group. Synchronized groups don't have per-file `PBXFileReference` entries — they use `PBXFileSystemSynchronizedRootGroup` instead — so the lookup fails.

Even when generation doesn't crash, public and private header visibility is lost because the headers are never added to `PBXFileSystemSynchronizedBuildFileExceptionSet` entries on the synchronized group.

## Expected Behavior

1. **No crash**: Headers that belong to a buildable folder should be **skipped** in the standard headers build phase (they don't have standalone file references).
2. **Preserved visibility**: Public and private headers within a buildable folder should be expressed as entries in the synchronized group's exception set, so Xcode respects their visibility.

## Files to Look At

- `cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift` — generates the headers build phase; needs to filter out headers that belong to synchronized (buildable) folders
- `cli/Sources/TuistGenerator/Generator/TargetGenerator.swift` — sets up synchronized groups for buildable folders; needs to map target-level header visibility into exception set entries

After fixing the code, update the relevant agent configuration files to reflect any workflow changes that accompany this fix. The project's `AGENTS.md` documents how to build and test Swift changes with `xcodebuild` — make sure those instructions work correctly in environments without code signing set up (like CI or agent sandboxes).
