# Fix multi-byte character panic in markdown parser emphasis context

## Problem

The Biome markdown parser panics when parsing certain markdown inputs that contain multi-byte characters (emoji, CJK text like Japanese, Korean, Chinese) within inline contexts that involve links inside blockquotes.

For example, parsing a blockquote containing Japanese text with an inline link causes a panic at a string slice operation due to an invalid byte boundary:

```
> 💡 Biomeは、[Prettierのオプションに対する考え方](https://prettier.io/docs/en/option-philosophy)と同様のアプローチを採用しています。
```

The panic occurs because the inline source length calculation produces a byte offset that falls in the middle of a multi-byte character, which then causes a `&str` slice to panic.

## Expected Behavior

The parser should handle markdown containing any valid UTF-8 characters without panicking, including emoji and CJK characters in blockquotes, links, and emphasis contexts.

## Files to Look At

- `crates/biome_markdown_parser/src/syntax/inline/emphasis.rs` — contains the inline source length calculation used during emphasis context setup. A similar bug was previously fixed in `mod.rs` for the `inline_list_source_len` function; this file has an analogous function that was missed.
