# Task: Fix Incorrect Inline Link R_PAREN Token Range

## Problem

When parsing markdown inline links that have titles with trailing whitespace, the parser produces incorrect token ranges.

For example, parsing `[link](/uri "title"  )` produces:
- `R_PAREN@65..68 "  )"` — the trailing whitespace `  ` is incorrectly absorbed into the closing paren token

The correct output should be:
- `R_PAREN@67..68 ")"` — the whitespace is consumed into the title's content, and R_PAREN is just `)`

## Affected Code

The bug is in the markdown inline link parser. When a link has a title followed by whitespace/newlines before the closing `)`, the parser incorrectly handles the trailing whitespace. The whitespace should be consumed as part of the title's content, but instead it's being absorbed into the R_PAREN token's range.

## Verification

Run the markdown parser tests:
```bash
cargo test -p biome_markdown_parser
```

Specifically, the test `ok::ok::inline_link_whitespace_md` should pass after the fix.

The snapshot at `crates/biome_markdown_parser/tests/md_test_suite/ok/inline_link_whitespace.md.snap` should show corrected token ranges after the fix:
- Before fix: `R_PAREN@65..68 "  )"` (whitespace absorbed into R_PAREN)
- After fix: `R_PAREN@67..68 ")"` (whitespace in title content)

After fixing the code, run `cargo insta review` to update the snapshot, then verify the test passes.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
