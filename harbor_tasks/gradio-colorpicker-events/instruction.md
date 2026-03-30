# Fix: ColorPicker not firing focus, blur, or submit events

## Problem

The ColorPicker component does not trigger `focus`, `blur`, or `submit` events. Users who attach event handlers like `.focus()`, `.blur()`, or `.submit()` to the ColorPicker component find that these callbacks are never called.

## Root Cause

After the Svelte 5 migration, the ColorPicker component still uses Svelte 4 legacy `on:` event directives (e.g., `on:click`, `on:focus`, `on:blur`, `on:mousedown`, `on:change`) in what is now a Svelte 5 runes-mode component. These legacy event directives do not work in Svelte 5 runes mode -- they must be replaced with native Svelte 5 event handler properties (`onclick`, `onfocus`, `onblur`, `onmousedown`, `onchange`).

Additionally, the submit event (firing on Enter key in the color text input) has no handler, and the focus/blur events on the dialog button are not wired up.

## Expected Behavior

- The ColorPicker should fire `focus` events when the color button gains focus
- The ColorPicker should fire `blur` events when focus leaves the component
- Pressing Enter in the color text input should fire a `submit` event
- All mouse interactions (click, mousedown, mousemove, mouseup) should work correctly

## Files to Investigate

- `js/colorpicker/shared/Colorpicker.svelte` -- event handler directives throughout the component
