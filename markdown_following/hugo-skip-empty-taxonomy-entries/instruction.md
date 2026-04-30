# Hugo: phantom taxonomy from `disableKinds = []` after `[taxonomies]`

You are working in a checkout of [Hugo](https://github.com/gohugoio/hugo) (a Go static-site generator) at `/workspace/hugo`.

## The bug

When a Hugo site's `hugo.toml` looks like this:

```toml
baseURL = "http://example.com/"
title = "Bug repro"
[taxonomies]
  tag = "tags"
disableKinds = []
```

then according to TOML's grouping rules `disableKinds` is parsed **inside** the `[taxonomies]` table (because it appears after the `[taxonomies]` header). Hugo therefore sees the taxonomies map as

```
{ "tag": "tags", "disableKinds": "" }
```

The empty-valued entry creates a "phantom" taxonomy whose internal `pluralTreeKey` is the empty string. Building any page that calls `.Ancestors` (e.g. `{{ range .Ancestors }}`) then loops indefinitely.

## What needs to happen

For a site whose `content/posts/hello.md` is rendered with the layout

```
Ancestors: {{ len .Ancestors }}|{{ range .Ancestors }}{{ .Kind }}|{{ end }}
```

the rendered `public/posts/hello/index.html` must contain exactly the substring

```
Ancestors: 2|section|home|
```

i.e. two real ancestors (the parent section and the home page) — no phantom taxonomy ancestor, and the build must terminate.

The fix should be applied to Hugo's configuration decoding so that **any taxonomy entry with an empty key OR an empty value is dropped** when the taxonomies map is built from user config. After the fix:

* A site whose TOML is "well-formed" (no leaked keys) keeps working unchanged.
* A site whose TOML accidentally leaks non-taxonomy keys into `[taxonomies]` (the case above) drops those leaked keys silently rather than producing a phantom taxonomy.
* Existing tests under `./config/allconfig/...` keep passing.

## Reference

* The bug reproducer is documented as Hugo issue **#14550**.
* The configuration decoders live under `config/allconfig/`.
* The `Taxonomies` field on the site config is a `map[string]string` of plural→singular labels (e.g. `{"tag": "tags", "category": "categories"}`).

## Code style requirements

This repository runs `./check.sh` as its quality gate. Your edits must:

* Be **`gofmt`-clean**. Any file you edit will be checked with `gofmt -l`.
* Pass **`go vet ./config/allconfig/...`**.
* Keep the existing tests under `./config/allconfig/...` passing (`go test -count=1 ./config/allconfig/...`).

## Style guidance from the repo's `AGENTS.md`

The repo's `AGENTS.md` (please read it) has rules that apply here, including:

* Brevity is good — for code, comments and commit messages.
* Don't comment the obvious; assume the reader is a Go expert.
* Use self-explanatory variable / function names. Use short names when context is clear.
* Never export symbols that are not needed outside of the package.
* Avoid global state.
* This is a project with a long history — look hard for an existing helper before writing a new one.
* In tests, use `qt` matchers (e.g. `b.Assert(err, qt.ErrorMatches, ...)`) instead of raw `if`/`t.Fatal` checks.
