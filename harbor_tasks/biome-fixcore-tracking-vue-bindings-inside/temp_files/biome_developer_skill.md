---
name: biome-developer
description: General development best practices for Biome
---

## inner_string_text()

Use `inner_string_text()` for extracting quoted string content, not `text_trimmed()`.

## quick_test

Use `quick_test` for AST inspection before implementing.

## EmbeddingKind

Use appropriate `EmbeddingKind` variants for embedded language tagging.

## Common Gotchas

- Use `let` chains to collapse nested `if let` statements
- Run `just l` before committing to catch clippy warnings
- Ask users before implementing deprecated/legacy syntax

| Method | Use When |
| --- | --- |
| `inner_string_text()` | Extracting quoted string content |
| `text_trimmed()` | Getting token text without whitespace |
