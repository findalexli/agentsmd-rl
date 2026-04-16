# Fix WYSIWYG Color Update on Theme Change

## Problem

When the Excalidraw theme changes between light and dark mode, the WYSIWYG text editor (the inline textarea that appears when editing text elements) does not update its text color to match the new theme. This causes text to become invisible or hard to read when switching themes while editing.

The WYSIWYG text editor is implemented in `packages/excalidraw/wysiwyg/textWysiwyg.tsx`.

## Expected Behavior

When a user is editing text in the WYSIWYG editor and the theme changes from light to dark (or dark to light):
1. The text color in the editor should immediately update to match the theme
2. The editor should apply the appropriate dark mode filter to the stroke color when in dark mode
3. When switching back to light mode, the original stroke color should be restored

To detect theme changes, the implementation must track the current theme state and compare it when state changes occur to determine if the theme has changed. The theme change detection mechanism should use the `app.onChangeEmitter` API to subscribe to state changes. When a change is detected that affects the theme, the `updateWysiwygStyle` function should be called to refresh the editor's styling.

The implementation must also properly clean up any subscriptions when the WYSIWYG editor is closed to prevent memory leaks.

## Development Notes

This is a Yarn-based monorepo. Key commands:
- `yarn test:typecheck` - TypeScript type checking
- `yarn test:update` - Run tests with snapshot updates
- `yarn fix` - Auto-fix formatting and linting

The project uses Vitest for testing.
