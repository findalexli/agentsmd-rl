# Fix GitInfo handling for modules with missing Origin

## Problem

When Hugo's GitInfo feature is enabled and the project uses Hugo modules, there's an issue with modules where the `Origin` field is not populated by `go list`. This happens in certain cases (see golang/go#67363).

Currently, when a module's Origin is nil or empty, the GitInfo code doesn't handle this gracefully, which can lead to:
1. Incorrect detection of whether the project itself is a Git module
2. Missing or incorrect Git information for content files from such modules

## What Needs to be Fixed

You need to make the following changes to properly handle modules with missing Origin information:

### 1. modules/module.go
Add a method to check if a `ModuleOrigin` is "zero" (empty/uninitialized). This should check if the essential fields are set.

### 2. modules/client.go
When `go list` returns a module with `Origin` set to nil, the code should attempt to load the Origin information from the `.info` JSON file. These files are located alongside the `.mod` files in the module cache and contain the missing Origin data in JSON format.

### 3. hugolib/gitinfo.go
Update the logic that detects whether the project itself is a Git module to also check if the module's Origin is valid (not zero). The current code only checks if `mod.Owner() == nil` but doesn't verify that Origin data is available.

### 4. hugolib/hugo_sites.go
Change the error handling in `loadGitInfo()` to return errors instead of just logging them. This ensures that GitInfo failures are properly propagated rather than silently ignored.

## Key Files to Modify

- `modules/module.go` - Add IsZero() method to ModuleOrigin
- `modules/client.go` - Load Origin from .info file when nil
- `hugolib/gitinfo.go` - Check Origin validity before using it
- `hugolib/hugo_sites.go` - Return error instead of logging

## Hints

- The `.info` JSON files have a structure like: `{"Version":"...","Time":"...","Origin":{"VCS":"git","URL":"...","Hash":"..."}}`
- You can derive the `.info` filename from the `.mod` filename by replacing the suffix
- Make sure to handle edge cases where files might not exist
- The fix should be defensive - don't fail the entire build if GitInfo has issues with modules, but do return errors properly from loadGitInfo

## Testing

After implementing the fix:
1. The code should compile without errors
2. A `ModuleOrigin` with empty URL should report as zero
3. The modules package should handle nil Origin gracefully
4. The gitinfo package should check Origin validity
