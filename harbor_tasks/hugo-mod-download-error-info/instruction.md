# Surface JSON error info from `go mod download` failures

You are working in a checkout of the [Hugo](https://github.com/gohugoio/hugo)
static site generator at `/workspace/hugo`.

## The bug

Hugo can declare module dependencies in `hugo.toml` under `[[module.imports]]`.
At config-load time, Hugo invokes `go mod download -json <path>@<version>` to
materialise each declared module. When that command fails — for example if the
module path points at a repository that does not exist, or a private repo with
no credentials — Hugo currently surfaces an error that drops the most useful
information.

The Go toolchain is intentionally helpful here: when invoked with `-json`,
`go mod download` writes a JSON document to **stdout** even on failure, of the
shape:

```json
{
  "Path": "github.com/bep/this-is-a-non-existing-repo",
  "Version": "main",
  "Error": "github.com/bep/this-is-a-non-existing-repo@main: invalid version: git ls-remote -q --end-of-options https://github.com/bep/this-is-a-non-existing-repo … exit status 128:\n\tfatal: could not read Username for 'https://github.com': terminal prompts disabled\nConfirm the import path was entered correctly.\nIf this is a private repository, see https://golang.org/doc/faq#git_https for additional information.\n"
}
```

(Note that `go mod download -json` writes the error as the JSON top-level
`Error` field — a plain string. This is **different** from `go list -m -json`,
which uses a nested `{"Err": "…"}` object.)

Today, Hugo discards that JSON. The user only sees a generic execution
failure that does not tell them the module path was invalid, that authentication
was attempted, or that they should consult Go's docs on private repos. This
makes module-import failures very hard to debug.

## Expected behaviour

When `go mod download -json` fails, the error returned from
`Client.downloadModuleVersion` (and therefore propagated up through Hugo's
module loader) **must include** the JSON `Error` field's content alongside
the existing wrapping error. Concretely, when run against a non-existing
private repository like `github.com/bep/this-is-a-non-existing-repo@main`,
the error message returned by Hugo must:

- still mention the module path and version (`github.com/bep/this-is-a-non-existing-repo@main`),
- contain the substring `mod download`,
- contain the substring `invalid version`,
- contain the substring `repository`,
- and contain these substrings in that order (so a regex of the form
  `(?s).*mod download.*invalid version.*repository.*` matches the error).

The fallback path (when the JSON cannot be decoded, or contains no `Error`)
must continue to wrap the underlying execution error as it does today, so
that no information is lost on non-JSON failures.

See the upstream issue [#14543](https://github.com/gohugoio/hugo/issues/14543)
for context.

## Where to look

The relevant code is in the `modules` package — search for where Hugo invokes
`go mod download -json` and constructs the wrapping error on failure. The
`goModule` / `goModuleError` types in the same file describe the JSON shape
for `go list -m -json`; you may need a separate decoding step for the
`Error`-string shape that `go mod download -json` actually emits.

## Verifying your fix locally

The repository's own test suite exercises the affected code paths:

```
go vet ./modules/... ./hugolib
go build ./modules/... ./hugolib
go test -count=1 -timeout 60s ./modules/
```

A behavioural test in `hugolib` invokes Hugo end-to-end with a non-existing
module import and asserts the resulting error matches the regex above.

## Code Style Requirements

This repository enforces the following on any file you edit:

- `gofmt` must be clean — run `gofmt -w` over edited files before submitting.
- `go vet ./modules/... ./hugolib` must succeed.
- No `hdebug.Printf` (or any other temporary debug-print) calls left in
  committed code — Hugo's CI fails if it sees one.

Hugo's `AGENTS.md` additionally asks contributors to:

- keep the code brief and avoid comments that restate what self-explanatory
  names already convey,
- use short variable names where the surrounding context is clear,
- avoid exporting symbols that are not needed outside the package,
- avoid global state,
- look for an existing helper before adding a new one.

Follow those conventions when shaping your fix.
