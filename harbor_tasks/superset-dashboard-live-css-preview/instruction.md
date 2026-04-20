# Add Live CSS Preview to Dashboard Properties Modal

## Problem

The Dashboard PropertiesModal currently only applies CSS changes when the user clicks "Save" or "Apply". Users want to see CSS changes reflected on the dashboard in real-time as they type in the CSS editor, with a debounce to avoid excessive re-renders. Additionally, when users click "Cancel", any previewed CSS changes should be reverted to the original value from when the modal opened.

## Requirements

1. **Live CSS Preview with Debounce**: As users type in the CSS editor, changes should be reflected on the dashboard after a 500ms debounce period. The CSS change should be dispatched to Redux so the dashboard updates immediately.

   Implementation must include:
   - A `useRef` named `originalCss` with type `string | null` to store the original CSS value when the modal opens
   - A `useRef` named `cssDebounceTimer` with type `ReturnType<typeof setTimeout> | null` to manage the debounce timer
   - A `useCallback` named `handleCustomCssChange` that implements the debounce logic
   - The debounce timer must be set with `setTimeout` using a 500ms delay
   - The CSS must be dispatched using `dashboardInfoChanged({ css })` imported from `src/dashboard/actions/dashboardInfo`

2. **Cancel Reverts Changes**: When the user clicks "Cancel", any pending debounce timers must be cleared and the original CSS value (from when the modal opened) must be restored by dispatching it to Redux.

   Implementation must include:
   - A `handleOnCancel` function (defined with a function body, not as an arrow function pointing directly to `onHide`)
   - Clearing of `cssDebounceTimer.current` using `clearTimeout`
   - Reference to `originalCss.current` to access the stored original value
   - Dispatch of `dashboardInfoChanged({ css: originalCss.current })` to restore the original CSS

3. **Cleanup on Unmount**: Any pending debounce timers must be cleared when the component unmounts.

   Implementation must include:
   - A `useEffect` with an empty dependency array that returns a cleanup function
   - The cleanup function must clear `cssDebounceTimer.current`

4. **Capture Original CSS Once**: When the modal opens (the `show` prop becomes true), the original CSS value should be captured. This should happen only once per modal open — subsequent data reloads within the same modal session should not overwrite the captured value.

   Implementation must include:
   - Logic to reset `originalCss.current = null` when the modal opens (when `show` becomes true)
   - A null check `if (originalCss.current === null)` before capturing the original CSS to prevent overwriting

5. **TypeScript Type Safety**: New code should not use explicit `any` types, following the project's AGENTS.md guidelines.

   Implementation must NOT use:
   - `useRef<any>`
   - `useRef<any[]>`
   - Any other explicit `any` type annotations in new code

6. **Handler Wiring**: The CSS editor component must receive the debounced handler.

   Implementation must include:
   - The `onCustomCssChange` prop of the child component must be set to `{handleCustomCssChange}`
   - The `setCustomCss` function should still be called within `handleCustomCssChange` to update local state

7. **Existing Tests Pass**: All existing PropertiesModal tests, lint checks, and TypeScript compilation must continue to pass.

## File to Modify

- `superset-frontend/src/dashboard/components/PropertiesModal/index.tsx`

## Context

- The dashboard uses Redux for state management. CSS changes need to be dispatched to Redux to be reflected on the dashboard in real-time.
- The child component that renders the CSS editor accepts an `onCustomCssChange` prop for handling CSS input changes.
- The modal has a `show` prop that becomes true when the modal opens.
- The existing code already manages local CSS state and dispatches changes on save/apply.
