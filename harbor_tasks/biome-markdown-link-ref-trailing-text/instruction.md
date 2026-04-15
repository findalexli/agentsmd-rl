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

## Verification

The task is verified by running a checker that parses markdown input and inspects the syntax tree. The checker outputs:
- `LINK_REF_DEF` when the syntax tree contains a `MD_LINK_REFERENCE_DEFINITION` node
- `NOT_LINK_REF_DEF` otherwise

The following inputs must produce `NOT_LINK_REF_DEF`:
- `[label]: /url invalid`
- `[a]: /url not-title`
- `[b]: /url some extra text`
- `[c]: http://example.com garbage`

The following inputs must produce `LINK_REF_DEF`:
- `[d]: /url "title"`
- `[e]: /url 'title'`
- `[f]: /url (title)`
- `[g]: /url`
