# Move Auto-Accept Permissions Toggle to Settings

## Problem

The auto-accept permissions toggle is currently embedded in the composer's prompt input area (`packages/app/src/components/prompt-input.tsx`). It appears as a shield icon button with `data-action="prompt-permissions"` that uses `aria-pressed` to track state. This clutters the composer with a control that logically belongs in the application settings.

The toggle, its label memo (`acceptLabel`), and handler (`toggleAccept`) all live inside `PromptInput`, along with the corresponding JSX (a `TooltipKeybind`-wrapped `Button`). The `onMouseDown` handler on the composer wrapper also references this button's data-action for focus management.

## Expected Behavior

The auto-accept permissions control should be moved to the Settings page (`packages/app/src/components/settings-general.tsx`) as a `Switch` component inside a `SettingsRow`. The toggle should:

- Use a `data-action="settings-auto-accept-permissions"` attribute
- Read the current auto-accept state via the permission context
- Handle both session-level and directory-level toggling
- Properly decode the current directory from URL params
- Be disabled when no directory is available

The old button and its supporting code (`acceptLabel` memo, `toggleAccept` function, the JSX block, and the `onMouseDown` selector reference) must be fully removed from `prompt-input.tsx`.

The e2e tests in `packages/app/e2e/` also need updating to find the toggle in the settings dialog rather than in the composer.

## Files to Look At

- `packages/app/src/components/prompt-input.tsx` — the composer component where the toggle currently lives
- `packages/app/src/components/settings-general.tsx` — the settings page where the toggle should be added
- `packages/app/e2e/prompt/prompt-shell.spec.ts` — e2e test that interacts with the auto-accept toggle
- `packages/app/e2e/session/session-composer-dock.spec.ts` — e2e test for composer dock and auto-accept
