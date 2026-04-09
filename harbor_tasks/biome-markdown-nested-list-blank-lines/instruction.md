# Fix false diagnostic on nested lists with blank lines

## Problem

The Biome markdown parser emits a false "Expected a list item" diagnostic when nested list items are separated by two or more blank lines. For example, the following valid markdown triggers the diagnostic:

```markdown
- top
  - sub a


  - sub b
```

With a single blank line between `sub a` and `sub b`, parsing works correctly. But when there are two or more consecutive blank lines, the parser fails to recognize `sub b` as a sibling of `sub a` in the nested list.

The same issue occurs at deeper nesting levels and with any number of extra blank lines (two, three, etc.).

## Expected Behavior

Nested list items separated by any number of blank lines should parse without diagnostics. Both `sub a` and `sub b` should be recognized as siblings in the same nested list under `top`.

## Files to Look At

- `crates/biome_markdown_parser/src/syntax/list.rs` — contains the list parsing logic, including blank-line handling and indent tracking between list items
