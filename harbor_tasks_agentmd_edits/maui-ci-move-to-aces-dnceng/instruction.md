# Fix CI Pool Validation Errors by Moving to ACES/DNCEng Pools

## Problem

The `device-tests` and `ui-tests` pipelines have been failing with instant YAML validation errors since January 2026:

> **Could not find a pool with name NetCore-Public. The pool does not exist or has not been authorized for use.**

### Root Cause

Azure DevOps validates ALL pool name references in YAML at parse time, including parameter defaults. The `NetCore-Public` pool only exists in `dnceng-public`, not in `dnceng/internal` where these pipelines run. The pool names were hardcoded in parameters rather than using conditional internal/public selection.

## Expected Behavior

The pipeline YAML should:
1. Define separate pool parameters for internal (`dnceng`) and public (`dnceng-public`) projects
2. Use `System.TeamProject` conditionals to select the appropriate pool at runtime
3. Use ACES (Azure Compute Engineering Systems) pools for public builds
4. Use DNCEng (.NET Core Engineering) pools for internal builds
5. Pass Azure DevOps YAML validation in both internal and public projects

## Files to Look At

- `eng/pipelines/ci-uitests.yml` — UI tests pipeline definition (main file to fix)
- `eng/pipelines/ci-device-tests.yml` — Device tests pipeline definition (needs Windows pool fix)

## Key Changes Needed

1. In `ci-uitests.yml`:
   - Split `androidPool`, `iosPool`, `windowsPool`, `windowsBuildPool`, `macosPool` parameters
   - Create separate `*Internal` and `*Public` variants with appropriate pool definitions
   - Add conditional logic using `${{ if eq(variables['System.TeamProject'], 'internal') }}:`
   - Map pools appropriately:
     - Internal: `NetCore1ESPool-Internal`, `Azure Pipelines` (macOS images)
     - Public: `AcesShared` (with `ACES_VM_SharedPool_Tahoe` image), `NetCore-Public`

2. In `ci-device-tests.yml`:
   - Add conditional pool selection for Windows Device Tests section
   - Use `windowsPoolInternal` for internal project, `windowsPoolPublic` for public

## Testing

The fix should allow the YAML to pass Azure DevOps validation in both the internal `dnceng` project and the public `dnceng-public` project without pool validation errors.
