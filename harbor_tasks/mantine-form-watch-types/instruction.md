# Fix Type Inference in form.watch Callback

## Problem

In the `@mantine/form` package, the `form.watch` subscriber callback receives `previousValue` and `value` fields that lack proper TypeScript type constraints. These values are obtained from `getPath()` calls but are not narrowed to the correct form value types, resulting in overly permissive typing. Users of `form.watch` get no useful autocomplete or type safety for these callback parameters.

## Acceptance Criteria

The corrected code must satisfy all of the following:

1. **Type-only import**: The modified source file must include this import declaration:
   ```
   import type { FormPathValue, LooseKeys } from './paths.types';
   ```

2. **Type assertions on watch callback values**: The watch subscriber callback payload must narrow `previousValue` and `value` using `as FormPathValue<Values, LooseKeys<Values>>` type assertions. The corrected source must contain these exact patterns:
   - `previousValue: getPath(path, previousValues) as FormPathValue<`
   - `value: getPath(path, $values.refValues.current) as FormPathValue<`
   - `LooseKeys<Values>`

3. **Runtime behavior unchanged** — only type annotations are being added; the JavaScript behavior must remain identical.

## Verification

After your changes:
- ESLint should pass on the modified file
- Existing Jest tests for `@mantine/form` should continue to pass
