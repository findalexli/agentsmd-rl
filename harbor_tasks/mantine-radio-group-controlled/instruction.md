# Radio.Group Controlled Mode Bug

## Issue

GitHub Issue: [mantinedev/mantine#8452](https://github.com/mantinedev/mantine/issues/8452)

When using `Radio.Group` in **controlled mode** (with `value` and `onChange` props), switching between radio options for the first time causes React to log the following error to the console:

```
A component is changing a controlled input to be uncontrolled.
This is likely caused by the value changing from a defined to undefined,
which should not happen.
Decide between using a controlled or uncontrolled input element for the lifetime of the component.
```

## Symptom

The bug manifests when:

1. A `Radio.Group` is rendered with `value` and `onChange` props (controlled mode)
2. The user clicks a different radio option within the group
3. React logs the controlled/uncontrolled warning on the first switch

## Expected Behavior

A `Radio.Group` used in controlled mode should:
- Accept and respond to the `value` prop
- Call `onChange` when the selection changes
- NOT trigger any React controlled/uncontrolled warnings

## Affected Component

The bug is in the `Radio` component implementation at:
`packages/@mantine/core/src/components/Radio/Radio.tsx`

When a `Radio` is used inside a `Radio.Group`, it receives context values for the group's state. The issue is related to how the component handles the `checked` state when transitioning between values in controlled mode.

## Note

- This bug affects only the controlled usage of `Radio.Group` (when `value` and `onChange` are provided)
- Uncontrolled usage (using `defaultValue` without `value`) is not affected
- The fix should ensure the controlled/uncontrolled transition does not occur

## Verification

To confirm the fix is properly applied:

1. **Radio.tsx** must contain a variable named `contextChecked` that tracks whether the component has received a checked value from context. This variable is necessary to avoid the controlled→uncontrolled transition that triggers React's warning.

2. **Radio.test.tsx** must contain a test case with the title:
   `"does not log controlled/uncontrolled warning inside controlled Radio.Group"`
   This test verifies the warning no longer occurs when switching options in a controlled group.

The pass-to-pass checks (prettier, eslint, TypeScript parse) verify the code is syntactically valid and properly formatted.