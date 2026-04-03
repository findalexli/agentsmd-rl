# Automate Widgetbook macOS Bundle Build and Release

## Problem

The Widgetbook macOS app bundle currently has no automated build or distribution pipeline. Developers must manually run Flutter build commands, package the `.app` into a zip, and upload it to GitHub Releases for review. There are no convenience Make targets and no CI automation for this.

## What's Needed

1. **Build script** — Create a shell script at `tool/widgetbook/build_macos_bundle.sh` that:
   - Builds the Widgetbook macOS app bundle from `lib/widgetbook.dart`
   - Packages it into a zip for distribution
   - Supports flags to skip the build step (upload-only) and to upload to a rolling GitHub Release via `gh`
   - Validates that it's running on macOS before proceeding
   - Follows the project's convention of using `fvm` when available

2. **Makefile targets** — Add convenience Make targets for building, uploading (without rebuild), and full build+publish workflows that invoke the build script with appropriate flags.

3. **CI workflow** — Create a GitHub Actions workflow that automatically builds and publishes the Widgetbook macOS bundle on pushes to the `main` branch, using a rolling prerelease tag.

4. **Documentation** — After adding the build tooling, update the relevant feature README to document the new export workflow, including the make commands, output locations, and any usage notes (e.g., macOS unsigned app handling).

## Files to Look At

- `Makefile` — existing make targets for context on conventions
- `tool/` — existing tooling scripts
- `.github/workflows/` — existing CI workflows for reference
- `lib/features/design_system/README.md` — the feature README for the design system / widgetbook
- `AGENTS.md` — project conventions including fvm usage and README maintenance requirements
