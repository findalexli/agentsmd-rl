# Bug: ColorPicker returns inconsistent color formats

## Summary

The `ColorPicker` component in Gradio is documented to return hex strings (e.g. `#ff0000`) as its value, but in practice it returns different formats depending on how the user interacts with it:

- Clicking on the color gradient area produces raw `rgba(...)` strings with floating-point values like `rgba(49.836..., 105.875..., 134.618..., 1)`
- Typing an RGB value into the text input (e.g. `rgb(102, 0, 71)`) passes it through unchanged
- Typing an HSL value (e.g. `hsl(0, 10%, 20%)`) also passes it through unchanged
- Only directly editing the hex input produces the expected hex format

## Relevant Files and Components

The colorpicker is located in `js/colorpicker/shared/`. This directory contains:
- `utils.ts` — contains color conversion utilities including `hsva_to_rgba()` and `format_color()`. Uses `tinycolor2` library. Must export `hsva_to_rgba` and `format_color` functions with TypeScript types.
- `Colorpicker.svelte` — the component UI. Imports from `@gradio/atoms` (including `BlockTitle`) and uses Svelte `bind:value` directive for input handling.
- `events.ts` — exports a `click_outside` handler with TypeScript type annotations: `(arg: MouseEvent)` and return type `: void`.

## Bug Details

1. **Gradient click output format**: The `hsva_to_rgba()` function returns `rgba(r, g, b, a)` strings. It should return 6-digit hex strings (`#rrggbb`) since that's what the component promises to deliver.

2. **Text input passthrough bug**: When users type colors in the text input, the `onchange` handler directly assigns `e.currentTarget.value` to the component value. This passes through whatever format the user typed (RGB, HSL, named colors) instead of normalizing to hex.

3. **Missing color normalization**: There is no function in `utils.ts` that converts arbitrary color formats (RGB, HSL, named colors like "red", shorthand hex like "#f00") to 6-digit hex strings (`#rrggbb`). Such a function should be callable from the Svelte component and must have explicit TypeScript type annotations `(color: string): string`.

## Expected Behavior

- `hsva_to_rgba()` must return `#rrggbb` hex strings, not `rgba(...)` strings
- Any user input in the text field must be converted to hex format before setting the component value
- The color value sent to the backend must always be a 6-digit hex string (`#rrggbb`), regardless of how the user selects or inputs the color
- The display format (Hex/RGB/HSL toggle) should only affect what the user sees in the text input, not the underlying value
- Invalid color inputs must be handled gracefully (return a string, not throw an error)
- All exported functions in `utils.ts` and `events.ts` must have explicit TypeScript type annotations on parameters and return values

## Examples

A working normalization would convert:
- `'rgb(255, 0, 0)'` → `'#ff0000'`
- `'hsl(0, 100%, 50%)'` → `'#ff0000'`
- `'red'` → `'#ff0000'`
- `'#f00'` (shorthand hex) → `'#ff0000'`

## Related Issue

This was reported by users who noticed their color processing pipelines broke when they received `rgba(...)` strings instead of the expected `#rrggbb` hex format.
