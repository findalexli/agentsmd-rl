# Biome Markdown Parser Bug: Setext Heading Inside Blockquote

## The Problem

When markdown contains a setext heading inside a blockquote, the parser incorrectly treats it as a regular paragraph. For example:

```markdown
> Foo
> ---
```

This should parse as a blockquote containing a setext heading (an `<h2>`), but instead it's parsed as a paragraph containing literal text.

## Expected Behavior

- `> Foo\n> ---` should parse as a blockquote containing a setext heading (`<h2>`)
- `> Bar\n> ===` should parse as a blockquote containing a setext heading (`<h2>`)
- Nested blockquotes like `> > Nested\n> > ---` should also work correctly
- All existing markdown parser tests must continue to pass

## Tests to Verify

After implementing the fix, the following tests must pass:

1. A new unit test named `force_relex_at_line_start_produces_thematic_break` verifying that the lexer correctly produces thematic breaks at line start after consuming a blockquote prefix — this test must exist in the `biome_markdown_parser --lib` test suite
2. A new spec test named `setext_heading_in_blockquote` verifying that setext headings work inside blockquotes — this test must exist in the `biome_markdown_parser --test spec_tests` test suite
3. All existing `biome_markdown_parser` unit tests should continue to pass
4. All existing `biome_markdown_parser` integration tests should continue to pass
5. `biome_parser` crate tests should pass
6. `cargo clippy` should pass with no warnings
7. `cargo fmt --check` should pass
8. `cargo check` on both crates should pass
