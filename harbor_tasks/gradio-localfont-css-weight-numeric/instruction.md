# Bug: LocalFont generates invalid CSS font-weight values

## Summary

The LocalFont class generates `@font-face` CSS rules with **text** `font-weight` values like `Regular` and `Bold` instead of the required **numeric** values (`400`, `700`). Browsers ignore or misinterpret non-numeric font-weight values in `@font-face` declarations, causing font loading to silently fail.

Additionally, the theme generation script generates CSS with `url('static/fonts/...')` paths. This works when served from a Gradio backend, but the Gradio website serves static assets from a different root. There is no way to generate theme CSS with website-appropriate font paths.

## Requirements

### 1. Numeric font-weight values in CSS

The generated CSS must use numeric font-weight values (100-1000 range per CSS spec) instead of text names. Weight 400 must correspond to "Regular" font files and weight 700 must correspond to "Bold" font files. The CSS declaration must look like:
```css
font-weight: 400;  /* not font-weight: Regular; */
```

### 2. Custom weight lists

LocalFont must accept an optional `weights` parameter that accepts a tuple of numeric weight values (e.g., `(100, 300, 400, 700, 900)`). When provided, the stylesheet should include all specified weights.

### 3. Website path prefix flag

The theme generation script must support a `--website` command-line flag. When this flag is present, the script must rewrite font URL paths from `url('static/...)` to `url('/...)` in the generated CSS. Without the flag, the original `url('static/...)` paths must be preserved.

### 4. Path-weight pairing

The file paths in the generated CSS must continue to use text-based weight names (e.g., `IBM Plex Mono-Regular.woff2`) while the CSS `font-weight` declaration uses the corresponding numeric value.

## Reproduction

```python
from gradio.themes.utils.fonts import LocalFont

font = LocalFont("IBM Plex Mono")
result = font.stylesheet()
print(result["css"])
```

The generated CSS currently contains `font-weight: Regular;` and `font-weight: Bold;` instead of `font-weight: 400;` and `font-weight: 700;`. The `src: url(...)` paths also reference the file using the text weight name rather than separating the file-path weight from the CSS weight.
