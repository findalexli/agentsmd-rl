# Fix markdown parser: reject link reference definitions with trailing text after destination

## Problem

The Biome markdown parser incorrectly accepts link reference definitions that have non-title text following the destination URL. For example, the input:

```markdown
[invalid-trailing]: /url invalid
```

is being parsed as a valid link reference definition with destination `/url invalid`. Per CommonMark spec §4.7, after whitespace following the destination, only a title starter (`"`, `'`, or `(`) is valid. The word `invalid` is not a valid title delimiter, so the entire line should be treated as a regular paragraph, not a link reference definition.

This also affects other similar patterns like `[label]: /url some extra text` and `[label]: http://example.com garbage`.

## Expected Behavior

Lines like `[label]: /url invalid` should be parsed as regular paragraphs. Only lines with a valid title after the destination should be recognized as link reference definitions:

```markdown
[valid]: /url "Title"      ← valid link reference definition
[valid]: /url 'Title'      ← valid link reference definition  
[valid]: /url (Title)      ← valid link reference definition
[valid]: /url              ← valid (no title)
[invalid]: /url garbage    ← should be a paragraph, NOT a link ref def
```

## Files to Look At

- `crates/biome_markdown_parser/src/syntax/link_block.rs` — Contains `skip_destination_tokens`, the function that parses the destination portion of link reference definitions. The loop that scans destination tokens needs to correctly stop at whitespace boundaries when the following content is not a title.
