# Fix WYSIWYG Color Update on Theme Change

## Problem

When the Excalidraw theme changes between light and dark mode, the WYSIWYG text editor (the inline textarea that appears when editing text elements) does not update its text color to match the new theme. This causes text to become invisible or hard to read when switching themes while editing.

The WYSIWYG text editor is implemented in `packages/excalidraw/wysiwyg/textWysiwyg.tsx`.

## Expected Behavior

When a user is editing text in the WYSIWYG editor and the theme changes from light to dark (or dark to light):
1. The text color in the editor should immediately update to match the theme
2. The editor should apply the appropriate dark mode filter to the stroke color when in dark mode
3. When switching back to light mode, the original stroke color should be restored

## Implementation Requirements

The fix requires the following code changes in `packages/excalidraw/wysiwyg/textWysiwyg.tsx`:

### 1. Theme State Tracking Variable

After the `textPropertiesUpdated` function ends (before the `updateWysiwygStyle` function), add a variable to track the current theme state:

```typescript
let LAST_THEME = app.state.theme;
```

This variable stores the current theme so it can be compared when state changes.

### 2. Update Theme Tracking in Style Function

At the beginning of the `updateWysiwygStyle` function (before any other logic), update the theme tracking variable:

```typescript
LAST_THEME = app.state.theme;
```

### 3. Subscribe to State Changes

Before the `// handle updates of textElement properties of editing element` comment, add a subscription to detect theme changes:

```typescript
// FIXME after we start emitting updates from Store for appState.theme
const unsubOnChange = app.onChangeEmitter.on((elements) => {
  if (app.state.theme !== LAST_THEME) {
    updateWysiwygStyle();
  }
});
```

This subscribes to the app's change emitter and calls `updateWysiwygStyle()` whenever the theme changes.

### 4. Cleanup Subscription

In the cleanup section (before `unbindOnScroll();`), add the cleanup call:

```typescript
unsubOnChange();
```

This prevents memory leaks by unsubscribing when the editor is closed.

## Development Notes

This is a Yarn-based monorepo. Key commands:
- `yarn test:typecheck` - TypeScript type checking
- `yarn test:update` - Run tests with snapshot updates
- `yarn fix` - Auto-fix formatting and linting

The project uses Vitest for testing.