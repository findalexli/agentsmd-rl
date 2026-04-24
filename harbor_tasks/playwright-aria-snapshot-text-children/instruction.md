# Fix ARIA snapshot generation dropping informative text children

## Problem

When generating ARIA snapshots (e.g. via `toMatchAriaSnapshot`), text children that contain information not present in the element's accessible name are sometimes silently dropped from the snapshot output. The `textContributesInfo` function in the source is responsible for deciding whether a text child should appear in the rendered snapshot — it currently drops text in cases where it should not.

### Expected inclusion cases

These text children should appear in snapshots (text has information not in the name):

| Name | Text | Expected |
|---|---|---|
| `"Alpha Beta"` | `"7"` | included |
| `"Some Long Name"` | `"42"` | included |
| `"Click to Submit"` | `"!"` | included |

Text that partially overlaps the name but also carries unique information should also be included:

| Name | Text | Expected |
|---|---|---|
| `"Alpha Beta"` | `"Alpha 7"` | included |
| `"Save Document"` | `"Save 3"` | included |
| `"Loading Progress Bar"` | `"Loading 85%"` | included |

### Expected exclusion cases (existing behavior to preserve)

| Name | Text | Expected |
|---|---|---|
| `"Hello World"` | `"Hello"` | excluded |
| `"Foo Bar"` | `"Foo"` | excluded |
| `"anything"` | `""` | excluded |
| `""` | `"some text"` | included |

The source uses a `longestCommonSubstring` utility for determining text-name overlap. This utility and its call site must remain present in the source.

## File to Look At

- `packages/injected/src/ariaSnapshot.ts` — contains the `textContributesInfo` function that decides whether text children appear in the rendered snapshot

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
