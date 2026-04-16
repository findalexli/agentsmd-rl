# Add Live CSS Preview to Dashboard Properties Modal

## Problem

The Dashboard PropertiesModal currently only applies CSS changes when the user clicks "Save" or "Apply". Users want to see CSS changes reflected on the dashboard in real-time as they type in the CSS editor, with a debounce to avoid excessive re-renders. Additionally, when users click "Cancel", any previewed CSS changes should be reverted to the original value from when the modal opened.

## Requirements

1. **Live CSS Preview with Debounce**: As users type in the CSS editor, changes should be reflected on the dashboard after a 500ms debounce period. The CSS change should be dispatched to Redux so the dashboard updates immediately.

2. **Cancel Reverts Changes**: When the user clicks "Cancel", any pending debounce timers must be cleared and the original CSS value (from when the modal opened) must be restored by dispatching it to Redux.

3. **Cleanup on Unmount**: Any pending debounce timers must be cleared when the component unmounts, using a proper cleanup effect.

4. **Capture Original CSS Once**: When the modal opens (the `show` prop becomes true), the original CSS value should be captured. This should happen only once per modal open — subsequent data reloads within the same modal session should not overwrite the captured value.

5. **TypeScript Type Safety**: New code should not use explicit `any` types, following the project's AGENTS.md guidelines.

6. **Existing Tests Pass**: All existing PropertiesModal tests, lint checks, and TypeScript compilation must continue to pass.

## File to Modify

- `superset-frontend/src/dashboard/components/PropertiesModal/index.tsx`

## Context

- The dashboard uses Redux for state management. CSS changes need to be dispatched to Redux to be reflected on the dashboard in real-time.
- The child component that renders the CSS editor accepts an `onCustomCssChange` prop for handling CSS input changes.
- The modal has a `show` prop that becomes true when the modal opens.
- The existing code already manages local CSS state and dispatches changes on save/apply.
