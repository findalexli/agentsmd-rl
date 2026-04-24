# CSF4: Fix duplicate preview loading issue in Vitest

## Problem

When using CSF factories (CSF4) in Storybook's Vitest integration, the preview configuration file is loaded twice. This results in duplicate setup of project annotations and preview decorators, which can cause unexpected behavior such as decorators running twice, doubled global parameters, and other side effects from redundant initialization.

The issue is that the Vitest plugin has CSF4-specific logic that directly injects the preview file into the setup files list. Since the project annotations virtual module already handles these same annotations, this causes duplication.

## Expected Behavior

The preview configuration should only be loaded once — through the project annotations virtual module that handles deduplication internally. There should be no CSF4-specific code path that bypasses this deduplication mechanism.

## Required Changes

### 1. Modify `code/addons/vitest/src/vitest-plugin/utils.ts`

The `requiresProjectAnnotations` function determines whether project annotations need to be loaded. It currently accepts a third parameter related to CSF4 detection. This parameter must be removed — the function should only accept two parameters: `testConfig` and `finalOptions`.

After the fix:
- The function signature should have exactly 2 parameters
- There should be no references to CSF4-related identifiers in the function body
- The function should return `true` by default (project annotations should always be loaded unless a setup file explicitly handles them)

### 2. Modify `code/addons/vitest/src/vitest-plugin/index.ts`

The plugin constructs a list of internal setup files. Currently, it detects CSF4 usage and conditionally adds the preview file to this list. This CSF4-specific detection and injection logic must be removed.

After the fix:
- The plugin should not load the preview file directly for setup file injection
- The `areProjectAnnotationRequired` variable and the `setup-file-with-project-annotations` module reference should be preserved
- The conditional inclusion of project annotations based on `areProjectAnnotationRequired` should still work

## Files to Look At

- `code/addons/vitest/src/vitest-plugin/index.ts` — The main Vitest plugin that constructs the list of internal setup files
- `code/addons/vitest/src/vitest-plugin/utils.ts` — Utility function `requiresProjectAnnotations` that determines whether project annotations need to be loaded