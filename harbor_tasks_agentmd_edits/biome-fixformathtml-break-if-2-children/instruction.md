# fix(format/html): break if >2 children, and at least one is not whitespace sensitive

## Problem

The HTML formatter does not correctly break a block-like element if it has more than 2 children, and at least one of them is another block-like element.

For example, this input:
```html
<div>a<div>b</div> c</div>
```

Is currently formatted as (incorrect):
```html
<div>a<div>b</div> c</div>
```

But should be formatted as (correct):
```html
<div>
  a
  <div>b</div>
  c
</div>
```

## Expected Behavior

The formatter should break block-like elements with >2 children when at least one child is not whitespace-sensitive. Specifically:

1. When a visible block-like element is adjacent to text, force multiline formatting
2. When a block-like element is followed by text (and we're already multiline), keep the text on its own line
3. `display: none` elements (like `<meta>`) should NOT trigger breaks to avoid introducing unwanted whitespace

## Files to Look At

- `crates/biome_html_formatter/src/html/lists/element_list.rs` — The main element list formatting logic
- `crates/biome_html_formatter/src/utils/css_display.rs` — CSS display utilities (check `is_block_like()`)
- `.claude/skills/prettier-compare/SKILL.md` — Skill for comparing with Prettier formatting

## Test Plan

1. The fix should handle the case `<div>a<div>b</div> c</div>` correctly
2. `display: none` elements like `<div>123<meta attr />456</div>` should NOT be broken (stays on one line)
3. `<details>` elements with summary and text should break properly

## Related Issues

Fixes #4927, #6407
