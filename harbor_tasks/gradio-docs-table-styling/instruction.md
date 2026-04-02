# Bug: Markdown tables on docs site have no styling

## Summary

Markdown tables rendered on the Gradio documentation website appear completely unstyled — no borders, no padding, no header differentiation, and no dark-mode support. The tables are functionally correct (the HTML is generated properly), but visually they are difficult to read because the raw `<table>`, `<th>`, and `<td>` elements have no CSS rules applied.

## Where to look

The website's global stylesheet is at:

```
js/_website/src/lib/assets/style.css
```

This file already contains some scoped table styling for specific containers (e.g., `.obj .max-h-96.overflow-y-scroll table ...`), but there are **no general-purpose table rules** that would apply to markdown-rendered tables elsewhere on the docs pages.

## Expected behavior

Tables on docs pages should have:
- Proper width, spacing, and collapsed borders
- Visually distinct header rows (background color, bold text)
- Consistent cell padding and borders
- Dark-mode variants that match the site's existing dark theme

## Reproduction

Visit any documentation page that contains a markdown table. The table content is present but renders as plain unstyled HTML elements.
