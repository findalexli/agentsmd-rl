# Prisma JSON Protocol Deserialization Bug

## Symptom

The JSON protocol layer in `@prisma/client-engine-runtime` does not correctly handle all tagged value types during deserialization and normalization. The following issues are present:

1. **Missing function export**: The package does not export a function named `deserializeJsonObject`. Attempting to import it yields `undefined` — the existing deserialization function has a different name.

2. **"Raw" tagged type causes error**: When `deserializeJsonObject` receives a tagged value with `$type: "Raw"` (e.g., `{ $type: "Raw", value: 42 }`), it throws an error about an unknown tagged value instead of returning the raw value directly (`42`).

3. **"FieldRef" and "Enum" types not handled by normalization**: The `normalizeJsonProtocolValues` function throws "Unknown tagged value" when it encounters:
   - `$type: "FieldRef"` — values like `{ $type: "FieldRef", value: { _ref: "test" } }` should pass through unchanged
   - `$type: "Enum"` — values like `{ $type: "Enum", value: "Active" }` should pass through unchanged

4. **Raw value wrapping defaults to disabled**: The raw value wrapping option in the JSON query serialization code defaults to disabled, causing raw values to lose type information during serialization. The default should be changed so raw values retain type information.

## Expected Behavior

After the fix:

- `deserializeJsonObject` is exported from `@prisma/client-engine-runtime` as a callable function
- `deserializeJsonObject({ $type: "Raw", value: 42 })` returns `42`
- `normalizeJsonProtocolValues({ $type: "FieldRef", value: { _ref: "test" } })` returns the input unchanged
- `normalizeJsonProtocolValues({ $type: "Enum", value: "Active" })` returns the input unchanged
- The raw value wrapping default is enabled in the JSON query serialization layer
- All existing `@prisma/client-engine-runtime` unit tests continue to pass
- The repo passes `pnpm run prettier-check` and `pnpm run check-engines-override`
