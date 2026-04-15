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

When parsing markdown with `parse_markdown(input)` from the `biome_markdown_parser` crate, the returned `Parse<MarkdocRoot>` result must return `false` from its `has_errors()` method for valid nested list structures with multiple blank lines.

## Files to Look At

- `crates/biome_markdown_parser/src/syntax/list.rs` — contains the list parsing logic, including blank-line handling and indent tracking between list items

## What to Verify

After fixing the bug, running `cargo test -p biome_markdown_parser` with the following test inputs should produce no parser errors:

- Input: `"- top\n  - sub a\n\n\n  - sub b\n"` (double blank lines between nested siblings)
- Input: `"- top\n  - sub a\n\n\n\n  - sub b\n"` (triple blank lines between nested siblings)
- Input: `"- top\n  - mid\n    - sub a\n\n\n    - sub b\n"` (three-level nesting with double blank lines at deepest level)
- Input: `"- top\n  - sub a\n\n  - sub b\n"` (single blank line — regression guard, should still pass)

The `has_errors()` method on the parse result must return `false` for all these cases.

## Important

Do not look at the `solution/` directory or attempt to read or apply patches from it. Work only from the problem description and codebase investigation.
