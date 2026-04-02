# Slow diagnostic rendering in ruff_annotate_snippets

## Bug Report

Diagnostic rendering in Ruff has regressed significantly in performance. Running `ruff check --select ALL` on the CPython test corpus shows that recent versions are about 2.5x slower than the 0.8 release, with diagnostic rendering being the dominant cost.

Profiling shows the bottleneck is in the rendering pipeline within the `ruff_annotate_snippets` crate, specifically in string-handling routines:

1. **`normalize_whitespace` in `crates/ruff_annotate_snippets/src/renderer/display_list.rs`** — This function processes every source line to replace tabs and Unicode control characters. It always allocates a new `String` even when the input contains none of the characters that need replacing, which is the overwhelmingly common case. For large codebases with thousands of diagnostics, this causes millions of unnecessary heap allocations.

2. **`StyledBuffer::render` in `crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs`** — The render method builds its output string incrementally without any size hint. It also uses formatting machinery (`write!` macro) for trivially simple operations like appending a single character or a newline, adding unnecessary overhead per character.

3. **`StyledBuffer::puts` in the same file** — This method writes a string into the buffer character-by-character through a general-purpose `putc` helper. Each call to `putc` independently checks and extends the line vector, duplicating work that could be done once for the entire string.

## Expected Behavior

Diagnostic rendering should avoid unnecessary allocations and redundant per-character overhead. The output should be identical — this is purely a performance issue.

## Relevant Files

- `crates/ruff_annotate_snippets/src/renderer/display_list.rs` — `normalize_whitespace` function and `OUTPUT_REPLACEMENTS` table
- `crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs` — `StyledBuffer::render` and `StyledBuffer::puts` methods
