# Fix Hugo's external source maps

You are working in the [Hugo](https://gohugo.io) static-site generator
repository at `/workspace/hugo`. Hugo runs CSS and JS through `esbuild` and
then post-processes the generated source map so that `sources` paths point
at the original on-disk files (Hugo resolves component paths through its own
plugin layer). This post-processing has two related bugs that drop or
mis-align entries in the produced source map.

## Symptoms

Build a Hugo site that imports several stylesheets and emit an external
linked source map, e.g.

```
-- assets/css/main.css --
@import "./foo.css";
@import "./bar.css" layer(mylayer);
@import './baz.css' screen and (min-width: 800px);
.main { background-color: red; }
-- assets/css/foo.css --
p { background: red; }
-- assets/css/bar.css --
div { background: blue; }
-- assets/css/baz.css --
span { background: green; }
```

Compile with `css.Build` using `sourceMap: "linked"`, `sourcesContent: true`,
and **`minify: false`** — the same options Hugo's own integration test uses.

Two things are wrong with the resulting `public/css/main.css.map`:

1. **Sources are silently dropped.** The `sources` array should contain four
   entries (`main.css`, `foo.css`, `bar.css`, `baz.css`) regardless of
   whether minification is on. Instead, with `minify: false`, almost every
   source is filtered out and you are left with an essentially empty
   `sources` array.

2. **`sourcesContent` falls out of alignment with `sources`.** Because the
   post-processing rewrites `sources` but leaves `sourcesContent`
   untouched, the *i*-th source no longer corresponds to the *i*-th content
   entry. In a downstream debugger this displays the wrong file's source
   when you click on a frame.

A correct fix makes `len(sources) == 4` for **both** `minify: true` and
`minify: false`, and keeps `sourcesContent` index-aligned with `sources`
(when `sourcesContent` is non-null). When the resolver drops a source, the
matching `sourcesContent` entry must also be dropped.

## Where the post-processing lives

The relevant code lives under `internal/js/esbuild/`. Two pieces interact:
the closure that `BuildClient.Build` hands to esbuild's output-fixup pass,
and a helper that rewrites the source-map JSON. Read both — the bug
involves their handoff.

In particular:

- The closure receives every path esbuild reports for the source map and
  decides what to substitute. Hugo has its own resolve plugin that may
  already supply an absolute on-disk filename, but the closure has a
  fallthrough that drops such paths instead of preserving them. Paths
  that point into esbuild's *output* directory (the value held by
  `opts.OutDir`) should still be dropped — those are emitted files, not
  input sources — but everything else that survived the earlier branches
  is a real source and must be kept.

- The source-map JSON helper currently rewrites only the `sources` slice.
  When entries are filtered out, the parallel `sourcesContent` slice has
  to be filtered the same way so that index *i* in one always matches
  index *i* in the other. When the input has no `sourcesContent`
  (null/empty), leave it that way.

A pre-existing helper named `paths.UrlFromFilename` is what converts an
absolute filename into the `file://` URL that ends up in the source map —
keep using it.

## Your task

Make the symptoms above go away. The fix should be confined to
`internal/js/esbuild/build.go` and `internal/js/esbuild/sourcemap.go`. Do
not modify any test files; the verifier owns those.

## Code Style Requirements

This repository runs `gofmt -l` and `go vet` as part of CI; both must come
back clean on the files you touch. The repo's `AGENTS.md` also asks that:

- Code be brief; comments only where the *why* is non-obvious.
- Variable and function names be self-explanatory; short names are fine
  when context is clear.
- No symbols be exported that are not needed outside the package.
- No stray debug printing be left behind. If you need temporary debug
  output during development, use `hdebug.Printf`, then remove it before
  submitting (CI fails on leftover `hdebug.Printf`).
- In tests, `qt` matchers are preferred over raw `if` / `t.Fatal`.

Run `./check.sh ./internal/js/esbuild/...` while iterating and
`./check.sh` once you think you're done; the verifier additionally runs
`gofmt -l` and `go vet ./internal/js/esbuild` and the package's existing
unit tests, all of which must remain clean.
