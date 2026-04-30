# Extract shared filter parameter parser from tags and statuses modules

## Problem

The `parseTagsParam` function in `code/core/src/manager-api/modules/tags.ts` and the `parseStatusesParam` function in `code/core/src/manager-api/modules/statuses.ts` contain nearly identical logic (~25-30 lines each) for parsing semicolon-separated URL filter parameters with `!`-negation support. This duplicated code violates DRY and makes maintenance harder — any fix to the parsing logic must be applied in two places.

## Expected Behavior

The shared parsing logic (semicolon splitting, empty-string guarding, `!`-prefix detection, and value transformation) should be extracted into a generic, reusable helper function.

Create a file at `code/core/src/manager-api/lib/filter-param.ts` containing a function named `parseFilterParam` exported from that module. The `parseFilterParam` function should:
- Accept a string value (which may be undefined or empty) and a transform function
- Split the input by semicolons (`;`)
- Filter out empty strings
- Route values with `!` prefix to an "excluded" array (stripping the `!`)
- Route other values to an "included" array
- Apply the transform function to each value
- Skip any values where the transform returns `null` or `undefined`
- Return an object with shape `{ included: string[], excluded: string[] }`

Both `parseTagsParam` and `parseStatusesParam` should be refactored to import and use this shared helper from `code/core/src/manager-api/lib/filter-param.ts`, reducing each to a one-liner that passes its specific transform. The public API of both functions must remain unchanged.

## Files to Look At

- `code/core/src/manager-api/modules/tags.ts` — contains `parseTagsParam` with inline parsing logic
- `code/core/src/manager-api/modules/statuses.ts` — contains `parseStatusesParam` with nearly identical inline parsing logic
- `code/core/src/manager-api/lib/filter-param.ts` — create this file to contain the shared `parseFilterParam` helper
