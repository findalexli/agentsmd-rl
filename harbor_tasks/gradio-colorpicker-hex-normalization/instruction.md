# Bug: ColorPicker returns inconsistent color formats

## Summary

The `ColorPicker` component in Gradio is documented to return hex strings (e.g. `#ff0000`) as its value, but in practice it returns different formats depending on how the user interacts with it:

- Clicking on the color gradient area produces raw `rgba(...)` strings with floating-point values like `rgba(49.836..., 105.875..., 134.618..., 1)`
- Typing an RGB value into the text input (e.g. `rgb(102, 0, 71)`) passes it through unchanged
- Typing an HSL value (e.g. `hsl(0, 10%, 20%)`) also passes it through unchanged
- Only directly editing the hex input produces the expected hex format

## Relevant Files

- `js/colorpicker/shared/utils.ts` — contains the `hsva_to_rgba()` conversion function and `format_color()` utility
- `js/colorpicker/shared/Colorpicker.svelte` — the component UI, including the text input's `onchange` handler

## Reproduction

1. Create a simple Gradio app with a `ColorPicker` component
2. Open the color picker dialog and click anywhere on the color gradient
3. Observe that the component's `value` is an `rgba(...)` string instead of a hex string
4. Switch to the RGB or HSL text input mode and type a value
5. Observe that the raw input string is passed as the value without normalization

## Expected Behavior

The component value sent to the backend should always be a hex string (`#rrggbb`), regardless of how the user selects or inputs the color. The display format (Hex/RGB/HSL toggle) should only affect what the user *sees* in the text input, not the underlying value.

## Related Issue

This was reported by users who noticed their color processing pipelines broke when they received `rgba(...)` strings instead of the expected `#rrggbb` hex format.
