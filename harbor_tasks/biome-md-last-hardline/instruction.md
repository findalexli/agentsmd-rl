# Fix markdown formatter: Remove last hard line break in paragraph

## Problem

Biome's markdown formatter preserves hard line breaks (two or more trailing spaces before a newline) unconditionally, including at the very end of a paragraph. This produces output that differs from Prettier.

For example, given this markdown input (where `·` represents a space):

```
aaa··
bbb··

```

Biome currently formats it as:

```
aaa··
bbb··

```

The trailing spaces on the last line (`bbb··`) are semantically meaningless — the paragraph boundary already terminates the content, so a hard line break there serves no purpose. Prettier removes these trailing spaces.

## Expected Behavior

The last hard line break before a paragraph ends should have its trailing space marker removed. Hard line breaks in the middle of a paragraph must be preserved.

Expected output:

```
aaa··
bbb

```

Only the last hard line's trailing spaces should be removed; middle hard line breaks (like on `aaa`) remain unchanged.

This also applies to single-line paragraphs:

```
foo··

```

Should become:

```
foo

```

## Files to Look At

- `crates/biome_markdown_formatter/src/markdown/auxiliary/hard_line.rs` — The `FormatMdHardLine` implementation that controls how `MdHardLine` syntax nodes are formatted
