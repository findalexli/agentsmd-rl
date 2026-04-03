# Fix HTML formatter: break elements with block-like children

## Problem

The Biome HTML formatter does not correctly handle parent elements containing a mix of text nodes and block-like child elements. Given:

```html
<div>a<div>b</div> c</div>
```

The formatter keeps everything on one line, but Prettier correctly breaks it:

```html
<div>
  a
  <div>b</div>
  c
</div>
```

Additionally, elements with `display: none` (like `<meta>`) should NOT trigger line breaks when adjacent to text content, since they don't affect visual layout:

```html
<!-- should stay on one line -->
<div>123<meta attr />456</div>
```

## Expected Behavior

- Block-like elements adjacent to text in a parent should trigger line breaks
- `display: none` elements should be left alone (no whitespace insertion)
- Prettier comparison snapshots should improve

## Files to Look At

- `crates/biome_html_formatter/src/html/lists/element_list.rs` — HTML element list formatting logic, handles whitespace and line break decisions between children
- `crates/biome_html_formatter/src/utils/css_display.rs` — CSS display type utilities including `is_block_like()`
- `crates/biome_html_formatter/tests/specs/html/whitespace/` — Whitespace-related test fixtures
- `crates/biome_html_formatter/tests/specs/prettier/html/tags/tags2.html.snap` — Prettier comparison snapshot

## Additional Task

The repository has a `packages/prettier-compare/` tool for comparing Biome and Prettier formatting output side-by-side, which is very useful when working on formatter changes. This tool currently lacks a Claude skill document. After fixing the formatter, create a `.claude/skills/prettier-compare/SKILL.md` that documents how to use this tool effectively. Review `packages/prettier-compare/README.md` for reference on its capabilities and usage patterns.
