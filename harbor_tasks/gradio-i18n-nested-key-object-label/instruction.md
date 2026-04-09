# Fix [object Object] when label matches nested i18n key

## Problem

When a Gradio component's `label` prop happens to match a top-level key in the translation dictionary that contains nested children (e.g., `label="file"` matches `{"file": {"uploading": "...", "download": "..."}}`), the component label renders as `[object Object]` in the UI instead of showing the intended label text.

This affects components like `gr.File(label="file")`, `gr.Audio(label="audio")`, or any component whose label collides with a nested i18n key structure. The `formatter` function in the core module is responsible for resolving translations.

## Expected Behavior

When a component label matches a top-level i18n key whose value is a nested object (not a plain string translation), the label should display the original text (e.g., "file") rather than the stringified object representation.

Normal i18n translations — where the translation value is a plain string — should continue to work as expected.

## Files to Look At

- `js/core/src/gradio_helper.ts` — Contains the `formatter` function that resolves translations for component labels
