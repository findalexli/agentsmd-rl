# Fix [object Object] when label matches nested i18n key

## Problem

When a Gradio component's `label` prop happens to match a top-level key in the translation dictionary that contains nested children (e.g., `label="file"` matches `{"file": {"uploading": "...", "download": "..."}}`), the component label renders as `[object Object]` in the UI instead of showing the intended label text.

This affects components like `gr.File(label="file")`, `gr.Audio(label="audio")`, or any component whose label collides with a nested i18n key structure. The `formatter` function in the core module is responsible for resolving translations.

## Expected Behavior

When a component label matches a top-level i18n key whose value is a nested object (not a plain string translation), the label should display the original text (e.g., "file") rather than the stringified object representation.

When `formatter` is called with a label that translates to an array value (e.g., `translate("items")` returns `["item1", "item2"]`), the formatter should return the original label string (e.g., "items").

When `formatter` receives `null` or `undefined`, it should return an empty string `""`.

Normal i18n translations — where the translation value is a plain string — should continue to work as expected.

The formatter function works with the `translate_i18n_marker` helper to handle i18n markers in format strings. The `I18N_MARKER` constant is `__i18n__` and markers follow the format `__i18n__{"key":"common.submit"}`. The formatter should resolve these markers by looking up the key in the translation dictionary and replacing the marker with the translated string (or leaving the marker unchanged if the key is not found or if the marker is malformed).

Malformed markers (e.g., `__i18n__` without JSON, `__i18n__{"key":"test.key"` with unclosed brace, or `__i18n__{invalid}` with invalid JSON) should return the original string unchanged.

## Files to Look At

- `js/core/src/gradio_helper.ts` — Contains the `formatter` function that resolves translations for component labels
