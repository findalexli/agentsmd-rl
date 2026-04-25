# Biome Markdown Parser Bug: Setext Heading Inside Blockquote

## The Problem

When markdown contains a setext heading inside a blockquote, the parser incorrectly treats it as a regular paragraph. For example:

```markdown
> Foo
> ---
```

This should parse as a blockquote containing a setext heading (an `<h2>`), but instead it's parsed as a paragraph containing literal text.

## Expected Behavior

Per CommonMark specification:
- `> Foo\n> ---` should parse as a blockquote containing a setext heading (`<h2>` with content "Foo")
- `> Bar\n> ===` should parse as a blockquote containing a setext heading (`<h1>` with content "Bar")
- Nested blockquotes like `> > Nested\n> > ---` should also work correctly
- The underlines (`---` or `===`) must be at the "line start" after the blockquote prefix (`> `) is stripped

## Tests to Verify

After implementing the fix, the following must pass:

1. A new unit test in `crates/biome_markdown_parser/src/lexer/tests.rs` that verifies the lexer correctly produces thematic breaks (for `---`) and setext heading underlines when re-lexing at line start after consuming blockquote prefixes

2. A new spec test in `crates/biome_markdown_parser/tests/spec_test.rs` that verifies setext headings work inside blockquotes (e.g., `> Foo\n> ---` parses as blockquote > setext heading, not paragraph)

3. All existing `biome_markdown_parser` unit tests should continue to pass

4. All existing `biome_markdown_parser` integration tests should continue to pass

5. `biome_parser` crate tests should pass

6. `cargo clippy` should pass with no warnings on the modified crates

7. `cargo fmt --check` should pass

8. `cargo check` on both `biome_markdown_parser` and `biome_parser` crates should pass

## Implementation Notes

The bug occurs because after consuming a blockquote prefix (`> `), the lexer's internal state no longer considers the following token to be at line start. This causes `---` to be lexed as regular minus tokens instead of being recognized as a thematic break or setext heading underline. The fix should ensure that after stripping the blockquote prefix, the lexer correctly handles line-start-sensitive tokens.
