# Fix Markdown Parser Panic on Multi-byte Characters

## Symptom

The Biome markdown parser panics when parsing markdown files containing multi-byte characters (like emoji or CJK characters) inside blockquotes with emphasis context. The panic message indicates a byte span calculation error when slicing source text during emphasis parsing.

When parsing content such as:
- Markdown with emoji (e.g., 💡) inside blockquotes with emphasis markers
- Markdown with CJK characters in emphasized text within blockquotes

The parser panics with a message about "byte index N is not a char boundary".

The issue is tracked as GitHub issue #9727.

## Root Cause

The `inline_list_source_len` function computes the source length of an inline list by accumulating individual token lengths. When multi-byte characters are present, the accumulated byte lengths can be incorrect because they don't account for the actual source positions, leading to invalid byte spans that cross character boundaries.

## Requirements

1. Fix the code in `crates/biome_markdown_parser/src/syntax/mod.rs` that computes inline source lengths:
   - Instead of accumulating individual token lengths, compute the length from actual source positions
   - The fix must avoid byte-boundary panics on multi-byte characters
2. The fix must not break the `biome_markdown_formatter` crate
3. All code must pass `cargo fmt` and `cargo clippy` checks
4. Add a regression test case for issue #9727 to the markdown parser test suite (`crates/biome_markdown_parser/tests/spec_test.rs`):
   - The test case must be labeled with the number "9727"
   - The test must include multi-byte character content (such as emoji 💡 or CJK text like こんにちは or 世界)

## Verification

After fixing, these should all pass:
- `cargo check -p biome_markdown_parser`
- `cargo test -p biome_markdown_parser -- spec_test`
- `cargo check -p biome_markdown_formatter`
- `cargo fmt --all -- --check`
- `cargo clippy --package biome_markdown_parser -- -D warnings`
