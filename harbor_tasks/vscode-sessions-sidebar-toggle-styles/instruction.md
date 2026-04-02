# Missing Visual Feedback for Sidebar Toggle Button

The sidebar toggle button in the agent sessions window currently lacks visual feedback when toggled on. When a user clicks the toggle button to enable a sidebar view, there's no visual indication that the button is in an active/checked state.

## Files to Look At

Look at the sidebar-related CSS in `src/vs/sessions/browser/parts/media/`. The sidebar part has styling for the title area and sidebar footer, but the toggle button's checked state appears to be missing.

## Expected Behavior

The toggle button should provide visual feedback when checked/toggled on:
- Apply a background color to indicate the active state
- Maintain the active appearance on hover and focus
- Use the correct VS Code theme variables for consistent styling

The toggle button is located in the sidebar's title area, specifically within the `global-actions-left` container.

## Note

This is a CSS-only change. No TypeScript or JavaScript modifications are required.
