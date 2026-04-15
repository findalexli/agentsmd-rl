# CSF4: Fix duplicate preview loading issue in Vitest

## Problem

When using CSF factories (CSF4) in Storybook's Vitest integration, the preview configuration file is loaded twice. This results in duplicate setup of project annotations and preview decorators, which can cause unexpected behavior such as decorators running twice, doubled global parameters, and other side effects from redundant initialization.

The issue occurs because the Vitest plugin detects CSF4 usage and directly injects the user's preview file into the internal setup files list, while the project annotations virtual module also provides these same annotations — leading to duplication.

## Expected Behavior

The preview configuration should only be loaded once, through the project annotations virtual module that handles deduplication internally. There should be no special-cased logic that directly injects the preview file as a setup file based on CSF4 detection.

## Required Changes

### 1. Modify `code/addons/vitest/src/vitest-plugin/utils.ts`

The `requiresProjectAnnotations` function must be modified to:
- Accept exactly **2 parameters**: `testConfig` and `finalOptions`
- **NOT accept an `isCSF4` parameter**
- Have **zero references to `isCSF4`** anywhere in its body
- Still be exported and async
- Return `true` by default (project annotations should always be loaded unless a setup file handles them)

### 2. Modify `code/addons/vitest/src/vitest-plugin/index.ts`

The plugin must be modified to:
- **NOT declare a `previewOrConfigFile` variable**
- **NOT conditionally add the preview file to setup files** (no `&& previewOrConfigFile` pattern)
- **NOT call `isCsfFactoryPreview()`** for CSF4 detection
- **NOT declare a `const isCSF4` variable**
- Preserve the `areProjectAnnotationRequired` variable and its usage
- Preserve the reference to `setup-file-with-project-annotations`

## Files to Look At

- `code/addons/vitest/src/vitest-plugin/index.ts` — The main Vitest plugin that constructs the list of internal setup files
- `code/addons/vitest/src/vitest-plugin/utils.ts` — Utility function `requiresProjectAnnotations` that determines whether project annotations need to be loaded
