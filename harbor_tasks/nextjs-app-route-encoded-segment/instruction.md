# Bug: URL-encoded dynamic placeholders not recognized as dynamic segments

## Problem

When an app route pathname contains URL-encoded square brackets (e.g., `%5B` for `[` and `%5D` for `]`), the route parser treats them as static segments rather than dynamic ones.

This causes fallback parameters to be missing for those segments, which leads to incorrect rendering when users navigate to pages with URL-encoded dynamic placeholders.

## Reproduction

Consider a route tree like `/[teamSlug]/[projectSlug]`. If a page is reached via a URL whose pathname contains encoded dynamic placeholders, the route parser should recognize them as dynamic segments. Instead, it treats them as literal static segments, so those parameters are never included in fallback params.

## Expected behavior

URL-encoded segments should be decoded before checking whether they match dynamic segment patterns. If decoding reveals a valid dynamic segment, it should be treated as dynamic. The following patterns must be recognized as dynamic when URL-encoded:

- Dynamic segment: `%5BparamName%5D` (decodes to `[paramName]`)
- Catchall: `%5B...paramName%5D` (decodes to `[...paramName]`)
- Optional catchall: `%5B%5B...paramName%5D%5D` (decodes to `[[...paramName]]`)

The parser must not crash on malformed encodings such as unclosed brackets (`%5Bparam`), partial percent sequences (`%5`), or stray percent signs (`100%25complete`).

## Requirements

1. The solution must use ES imports only — no bare `require()` calls (see AGENTS.md guidelines).
2. The solution must not contain hardcoded secret values such as API keys, tokens, or credentials (see AGENTS.md guidelines).
3. The fix must not break existing non-encoded dynamic segment parsing, static segment parsing, or introduce crashes on malformed input.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
