# Bug: ColorPicker returns inconsistent color formats

## Summary

The `ColorPicker` component in Gradio is documented to return hex strings (e.g. `#ff0000`) as its value, but in practice it returns different formats depending on how the user interacts with it:

- Clicking on the color gradient area produces raw `rgba(...)` strings with floating-point values like `rgba(49.836..., 105.875..., 134.618..., 1)`
- Typing an RGB value into the text input (e.g. `rgb(102, 0, 71)`) passes it through unchanged
- Typing an HSL value (e.g. `hsl(0, 10%, 20%)`) also passes it through unchanged
- Only directly editing the hex input produces the expected hex format

## Relevant Files and Components

The colorpicker is located in `js/colorpicker/shared/`. This directory contains:
- `utils.ts` — contains color conversion utilities including `hsva_to_rgba()` and `format_color()`
- `Colorpicker.svelte` — the component UI, which should import from `@gradio/atoms` (including `BlockTitle`) and have input handling with `bind:value` or `onchange`
- `events.ts` — must export a `click_outside` handler with TypeScript type annotations for parameters (e.g., `Node`, `MouseEvent`) and return type (`void`)

## Required Changes

1. **Color normalization function**: Create a `normalize_color` function in `utils.ts` that converts any valid color format (RGB, HSL, named colors like "red", shorthand hex like "#f00") to a 6-digit hex string (`#rrggbb`). The function must have explicit TypeScript type annotations: `(color: string): string`.

2. **Gradient click output**: The color conversion that produces values when clicking the gradient must return hex strings (`#rrggbb`) instead of `rgba(...)` strings.

3. **Text input normalization**: The text input's change handler in the Svelte component must normalize user input to hex format before setting the component value, rather than passing raw input through unchanged.

## Expected Behavior

- `normalize_color('rgb(255, 0, 0)')` should return `'#ff0000'`
- `normalize_color('hsl(0, 100%, 50%)')` should return `'#ff0000'`
- `normalize_color('red')` should return `'#ff0000'`
- `normalize_color('#f00')` should return `'#ff0000'`
- The color value sent to the backend must always be a 6-digit hex string (`#rrggbb`), regardless of how the user selects or inputs the color
- The display format (Hex/RGB/HSL toggle) should only affect what the user sees in the text input, not the underlying value
- Invalid color inputs should be handled gracefully (return a string, not throw an error)

## Related Issue

This was reported by users who noticed their color processing pipelines broke when they received `rgba(...)` strings instead of the expected `#rrggbb` hex format.
