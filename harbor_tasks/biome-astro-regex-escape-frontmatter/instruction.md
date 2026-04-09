# Astro Frontmatter Fails to Parse Regex Literals with Escape Sequences

## Problem

When an Astro (`.astro`) file contains a regular expression literal with an escape sequence followed by a quantifier in the frontmatter block, the parser fails to correctly identify the closing `---` fence. For example, a file like:

```astro
---
const RE = /\d{4}/
---

<div />
```

produces parse errors or misidentifies the frontmatter boundary. The regex `/\d{4}/` is not recognized as a regex literal, which causes the closing `---` to be swallowed as part of the frontmatter content.

Other regex patterns with backslash escapes followed by curly-brace quantifiers (e.g., `/\w{2,3}/`) exhibit the same problem.

## Expected Behavior

The Astro frontmatter parser should correctly recognize regex literals that contain escape sequences (like `\d`, `\w`, `\s`) followed by quantifiers (like `{4}`, `{2,3}`). The frontmatter block should close cleanly at the second `---`, and the HTML content after it should parse normally.

## Files to Look At

- `crates/biome_html_parser/src/lexer/mod.rs` — Contains the `QuotesSeen` struct and its `check_byte` method, which tracks string/comment/regex state during frontmatter scanning. The issue is in the ordering of escape sequence handling relative to regex literal detection.
