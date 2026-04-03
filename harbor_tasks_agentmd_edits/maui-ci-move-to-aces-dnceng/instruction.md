# Migrate macOS CI to ACES shared pool and modernize build infrastructure

## Problem

The .NET MAUI CI pipelines currently use `Azure Pipelines` hosted images (`$(HostedMacImage)`, `macOS-15-arm64`) for macOS build and test jobs. These need to be migrated to the `AcesShared` pool with `ImageOverride` demands pointing to `ACES_VM_SharedPool_Tahoe`.

Additionally, the build infrastructure has several issues:

1. **`eng/Build.props`** lumps all project selection into a single flat `ItemGroup` with per-item conditions. This makes it impossible to have separate build logic for pack-only vs full-build scenarios. The file needs restructuring into distinct `ItemGroup` blocks: one for build tasks, one for pack-only (selecting Packages solution filters), one for full builds (selecting the main `.sln`/`.slnf`), and one for device tests. The full-build and pack sections should set `ValidateXcodeVersion=false` via `AdditionalProperties`.

2. **`eng/pipelines/common/provision.yml`** has a fragile Xcode version fallback — it only tries `major.minor.0` when the exact version isn't found. This should be improved to try a cascading chain: exact version, then `major.minor`, then just `major`. If none are found, it should exit with an error instead of proceeding with a likely-broken version.

3. **`eng/pipelines/arcade/stage-build.yml`** passes `-projects` and explicit `/p:` properties in the main solution build step. Since `Build.props` should now control project selection and properties, these explicit arguments should be removed.

4. **`eng/pipelines/arcade/stage-device-tests.yml`** uses Cake (`dotnet cake --target=dotnet`) to install the .NET SDK. This should use the Arcade build script (`build.cmd -restore`) instead.

5. **`eng/pipelines/device-tests.yml`** has overly restrictive `Agent.OSVersion` demands for iOS and Catalyst pools that should be removed.

6. **`eng/pipelines/ci.yml`** macOS pool definitions need updating from Azure Pipelines hosted to AcesShared.

## Expected Behavior

- All macOS CI jobs use the `AcesShared` pool with `ACES_VM_SharedPool_Tahoe` image demands
- `Build.props` cleanly separates pack, full-build, and device-test project selection
- Xcode provisioning gracefully falls back through version specificity levels
- Device test pipeline uses Arcade build scripts, not Cake
- Documentation reflects the new recommended build workflow

## Files to Look At

- `eng/Build.props` — MSBuild project selection logic
- `eng/pipelines/ci.yml` — CI pool definitions for macOS
- `eng/pipelines/common/provision.yml` — Xcode version selection and fallback
- `eng/pipelines/arcade/stage-build.yml` — Main build pipeline step
- `eng/pipelines/arcade/stage-device-tests.yml` — Windows device test SDK provisioning
- `eng/pipelines/arcade/stage-integration-tests.yml` — iOS test device config
- `eng/pipelines/device-tests.yml` — Device test pool demands
- `docs/DevelopmentTips.md` — Developer build instructions (update to reflect new workflow)
- `src/Workload/README.md` — Workload build instructions (update to reflect new workflow)

After making the infrastructure changes, update the relevant documentation to reflect the new recommended build approach using Arcade build scripts (`./build.sh -restore`) instead of Cake.
