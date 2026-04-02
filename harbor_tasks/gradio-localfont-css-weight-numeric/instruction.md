# Bug: LocalFont generates invalid CSS font-weight values

## Summary

The `LocalFont` class in `gradio/themes/utils/fonts.py` generates `@font-face` CSS rules with **text** `font-weight` values like `Regular` and `Bold` instead of the required **numeric** values (`400`, `700`). Browsers ignore or misinterpret non-numeric font-weight values in `@font-face` declarations, causing font loading to silently fail.

Additionally, the `scripts/generate_theme.py` script generates CSS with `url('static/fonts/...')` paths. This works when served from a Gradio backend, but the Gradio website (a SvelteKit app under `js/_website/`) serves static assets from a different root. There is no way to generate the theme CSS with website-appropriate font paths — the script needs a flag to adjust the URL prefix for the website context.

## Reproduction

```python
from gradio.themes.utils.fonts import LocalFont

font = LocalFont("IBM Plex Mono")
result = font.stylesheet()
print(result["css"])
```

The generated CSS will contain `font-weight: Regular;` and `font-weight: Bold;` instead of `font-weight: 400;` and `font-weight: 700;`. The `src: url(...)` paths also reference the file using the text weight name rather than separating the file-path weight from the CSS weight.

## Files to investigate

- `gradio/themes/utils/fonts.py` — `LocalFont.stylesheet()` method
- `scripts/generate_theme.py` — theme CSS generator script
- `js/_website/package.json` — website dev script that invokes `generate_theme.py`
