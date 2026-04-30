# Add `strings.ReplacePairs` to Hugo's templating

Hugo exposes a `strings` namespace of template functions to its template
language. Currently the namespace has `strings.Replace` (one old/new pair
plus an optional limit), but no convenient way to apply many replacements
at once. Users have asked for one.

Your task is to add a new function to the `strings` namespace named
`ReplacePairs` with the contract described below.

## Function signature

The function is a method on the `*Namespace` receiver in
Hugo's `tpl/strings` package. Its signature is variadic over `any`:

```go
func (ns *Namespace) ReplacePairs(args ...any) (string, error)
```

The **last** argument is always the source string (it may be any value
castable to a string, e.g. a Go `string`, a `template.HTML`, an `int`).

The arguments **before the last** are old/new replacement pairs, supplied
in either of two forms:

1. **Inline form** (3+ args): `ReplacePairs("a", "b", "c", "d", source)` —
   each odd-indexed arg is an *old* string, the next is its *new*
   replacement, and the last arg is the source.
2. **Slice form** (exactly 2 args): `ReplacePairs(pairs, source)` where
   `pairs` is a slice (`[]string` or `[]any`) of alternating old/new
   strings.

When invoked from a Go template, both forms work:

```go-html-template
{{ "aabbcc" | strings.ReplacePairs "a" "x" "b" "y" "c" "z" }}  →  xxyyzz
{{ "aabbcc" | strings.ReplacePairs (slice "a" "x" "b" "y" "c" "z") }}  →  xxyyzz
```

## Replacement semantics

Replacements are applied in a **single pass** over the source, in the
order pairs are listed. For example, with pairs `("app","pear")` then
`("apple","orange")` and source `"apple"`, the result is `"pearle"` —
`"app"` matches first and becomes `"pear"`, leaving `"pearle"` which is
no longer rescanned for `"apple"`.

Pair values may also be `template.HTML` or any type castable to a string
via Hugo's existing string-cast helper (e.g. `int` → `"42"`). Likewise
the source may be a `template.HTML` or any castable value.

If the source string is empty **or** there are zero pairs, the function
returns the source string converted to a Go `string`, with no error.

## Error contract

The function returns an `error` (and an empty `""` result) when:

- Fewer than 2 arguments are provided. The error message must contain
  the substring `requires at least 2`.
- Exactly 2 arguments are provided but the first is not a slice (e.g.
  `ReplacePairs("a", "s")` or `ReplacePairs(42, "s")`). The error
  message must contain the substring `first must be a slice`.
- The total number of pair elements is odd (e.g. inline
  `ReplacePairs("a", "b", "c", "s")` has three pair-elements before the
  source, or slice `ReplacePairs([]string{"a"}, "s")` has one). The
  error message must contain the substring `uneven number`.
- Any pair value, source value, or slice element is not castable to a
  string. (Hugo's existing string cast yields an error containing
  `unable to cast` for non-castable types.)

## Template registration

The function must also be **registered** in the `strings` namespace's
`init()` so that templates can call it as `strings.ReplacePairs`. Hugo
registers methods via `ns.AddMethodMapping(...)`. Registration must
include at least one example demonstrating the inline form and one
demonstrating the slice form. The expected template output for both
forms with input `"aab"` and pairs `("a","b","b","c")` is `bbc`.

## Performance hint (not required for correctness)

Calls with the same pairs are common (e.g. inside hot template loops).
A clean implementation reuses any precomputed work between calls with
identical pair sets. You are free to keep this simple if you prefer;
correctness is what the tests check.

## Code Style Requirements

- The repository's tests run `gofmt`; the modified files must be
  gofmt-clean (use `gofmt -w` or your editor's Go formatter on the
  files you change).
- The existing `tpl/strings/` test file uses the
  `github.com/frankban/quicktest` matchers (`qt.IsNil`,
  `qt.Equals`, `qt.ErrorMatches`). Any new test code should follow the
  same style.
- Follow the project's `AGENTS.md` guidance: keep comments brief, avoid
  exporting symbols not used outside the package, avoid global state,
  and reuse existing helper packages (look for them under
  `common/`) before introducing new ones.

## Verification

Your change should make the existing `tpl/strings` package continue to
build and pass `go test ./tpl/strings/`, and `go vet ./tpl/strings/...`
should remain clean.
