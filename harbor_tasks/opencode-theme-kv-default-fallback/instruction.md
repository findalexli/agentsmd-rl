# Theme fallback ignores saved preference from KV store

## Summary

When the TUI's currently active theme is not found in the loaded themes map (for example, a custom or plugin theme was removed, or hasn't loaded yet), the theme resolution logic falls back directly to the built-in `"opencode"` default theme. It skips checking the user's previously saved theme preference stored in the KV store.

This means a user who selected a theme (e.g., `"dracula"`) and then switched to a custom theme that was later removed will not see their saved `"dracula"` preference restored — they'll get the `"opencode"` default instead.

## Relevant File

`packages/opencode/src/cli/cmd/tui/context/theme.tsx`

Look at the `createMemo` that computes the resolved `values` (the active theme colors). The fallback chain when `store.themes[store.active]` is `undefined` goes straight to `store.themes.opencode` without consulting the KV store's `"theme"` key.

## Expected Behavior

When the active theme is not found in the themes map, the code should:

1. First, check the KV store for a saved theme name
2. If a valid saved theme exists in the themes map, use it
3. Only fall back to `"opencode"` as a last resort

## Hints

- The `kv` object is already available in scope (from `useKV()`)
- The saved theme key in KV is `"theme"`
- The fix should be in the `createMemo` callback that produces the resolved theme values
