# fix(ui): ansi colours — background-color leak on non-reverse text

## Problem

The `ansi2html` function in `packages/web/src/ansi2html.ts` incorrectly applies a `background-color` style to text that only has a foreground color specified. When callers pass `defaultColors` with both `fg` and `bg` properties, the `bg` value is unconditionally applied as `background-color` on every styled span — even when the text has no ANSI reverse-video code.

This causes console messages, error messages, and source line error widgets in the trace viewer and HTML reporter to have unwanted background fills. The UI shows colored text with an unexpected background color behind it.

## Expected Behavior

The `background-color` CSS property should only be set when ANSI reverse-video mode (`\x1b[7m`) is active. Non-reverse text should only get a `color` style from the `defaultColors.fg` property. All callers of `ansi2html` must pass appropriate `defaultColors` for their context (error, warning, or log).

## Files to Look At

- `packages/web/src/ansi2html.ts` — the core ANSI-to-HTML converter function; the background-color logic is wrong
- `packages/trace-viewer/src/ui/consoleTab.tsx` — calls `ansi2html` for console log/warning/error entries
- `packages/web/src/components/codeMirrorWrapper.tsx` — calls `ansi2html` for source error widgets
- `packages/web/src/components/errorMessage.tsx` — calls `ansi2html` for error message display
