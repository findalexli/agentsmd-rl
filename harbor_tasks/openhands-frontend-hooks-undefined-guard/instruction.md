# Fix Runtime Crash in Hooks Viewer Modal

## Problem

The hooks viewer modal in the OpenHands frontend crashes with a runtime error when the agent finishes but workspace hooks are still executing on the server. The API returns hook matcher data, but the frontend code that renders this data assumes certain fields are always present.

The error manifests as:
```
Cannot read properties of undefined (reading 'length')
```

This error occurs when the code tries to access properties on a `hooks` field that is `undefined` instead of an array.

## Scope

The crash occurs in code that renders hook matcher content in the conversation panel. The fix must ensure the frontend handles cases where the `hooks` field is missing from the server response.

## Expected Outcome

- The hooks modal opens without crashing when `hooks` is undefined
- TypeScript type checking passes
- All frontend tests pass
- Linting passes

## Verification

Run the frontend type checker and test suite:
```bash
cd frontend
npx tsc --noEmit
npm run test
```

If the fix is correct, the type checker will pass and all tests will run without runtime errors.