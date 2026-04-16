# Add .continue/checks/ discovery to cn review

## Problem

The `cn review` command currently only discovers local review files from `.continue/agents/*.md`. However, the documentation and quickstart guides tell users to create files in `.continue/checks/`, leading to confusion when `cn review` shows zero local reviews for users following the docs.

## Goal

Modify `resolveFromLocal()` in `extensions/cli/src/commands/review/resolveReviews.ts` to discover markdown files from both directories:

1. `.continue/agents/*.md` (existing behavior, unchanged)
2. `.continue/checks/*.md` (new - should also be scanned)

## Requirements

### Discovery from both directories
- The function must discover markdown files from both `.continue/agents/` and `.continue/checks/`
- Files with the same filename should not appear twice in the output
- When a file exists in both directories, the version from `agents/` should appear in the output (not the one from `checks/`)

### Deduplication approach
- The implementation needs a way to track which files have already been added to avoid duplicates
- A standard collection type for uniqueness tracking is appropriate for this purpose

### Comments and Documentation
- Update JSDoc comments to reference both `.continue/checks/*.md` and `.continue/agents/*.md`
- Document in the code that agents/ takes precedence over checks/ for duplicate files

### Error Handling
- The function should handle cases where either or both directories don't exist gracefully
- Use try/catch blocks around directory read operations

### Path Construction
- Construct the path to `.continue/checks` using `path.join()` with appropriate segments

## Testing

The repo uses Vitest for testing. Add unit tests in `resolveReviews.test.ts` covering:
- Discovery from agents/ only
- Discovery from checks/ only
- Discovery from both with deduplication
- Empty result when neither directory exists
- Graceful handling of read errors

## Files to Modify

- `extensions/cli/src/commands/review/resolveReviews.ts` - Update `resolveFromLocal()` function
- `extensions/cli/src/commands/review/resolveReviews.test.ts` - Add unit tests (new file)

## Context

- This is a TypeScript/Node.js CLI tool
- Uses Vitest for testing with ESM support
- Build command: `npm run build`
- Test command: `npm test`
- Lint command: `npm run lint`
- Format command: `npm run format`

## Verification

After your changes:
1. `npm run build` should compile successfully
2. `npm run lint` should pass type checking
3. `npm run format` should pass formatting checks
4. `npm test -- resolveReviews.test.ts --run` should pass all 5 test cases
