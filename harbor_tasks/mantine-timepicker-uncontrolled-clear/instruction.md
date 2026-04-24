# mantinedev/mantine#8622 — TimePicker clearing in uncontrolled mode

**Task**: Fix the TimePicker component so that clearing the time (via backspace in an uncontrolled TimePicker with `defaultValue`) properly calls `onChange` with an empty string `''`.

## Bug description

When a `TimePicker` is used in **uncontrolled mode** (i.e., has `defaultValue` but no `value` prop), clearing any time field with backspace should propagate an empty value via `onChange('')`. The original implementation only called `onChange` when the `value` prop was a non-empty string. Since `value` is `undefined` in uncontrolled mode, `onChange` was never called when clearing.

## Expected behavior

Given an uncontrolled TimePicker with `defaultValue="12:34"`:
- User clicks the hours input and presses backspace to clear it
- `onChange` is called with `''` (empty string) exactly once
- The component state reflects the cleared field

## Acceptance criteria

1. A new test `"calls onChange when cleared with backspace in uncontrolled mode"` is added to `packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx`
2. This test passes when the fix is applied
3. Existing TimePicker tests continue to pass: `yarn jest packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx --no-coverage` returns exit code 0

## Technical hints

- The fix involves tracking validity state in `use-time-picker.ts`
- `handleTimeChange` needs to handle the case where a field becomes invalid after user input
- `setTimeString` and `clear` may need validity tracking updates
- The solution should work for both `12h` and `24h` formats with and without seconds

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
