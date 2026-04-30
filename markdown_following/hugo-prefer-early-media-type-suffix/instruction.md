# Hugo: prefer earlier media-type suffixes when picking among equally-named templates

You are working in a checkout of the [Hugo](https://github.com/gohugoio/hugo)
static site generator at `/workspace/hugo`. Hugo lets a user declare multiple
*suffixes* for one media type, e.g.:

```toml
[mediaTypes.'text/html']
suffixes = ['b','a','d','c']

[outputFormats.html]
mediaType = 'text/html'
```

Here the user has told Hugo "for HTML, the canonical extension is `b`; the
others are also acceptable". The order of `suffixes` is significant: the
first entry is the preferred extension, the rest are alternates.

## The bug

When a user provides multiple layout templates that share the same base name
but differ only in their file extension — and *each* extension is a valid
suffix for the same media type — Hugo currently does **not** honour the
declared suffix order. Concretely, given:

```
content/p1.md
layouts/page.html.a
layouts/page.html.b
layouts/page.html.c
layouts/page.html.d
```

…with `suffixes = ['b','a','d','c']`, Hugo should render the page using
`layouts/page.html.b` (because `b` is the first declared suffix) and write
the result to `public/p1/index.b`.

In the current code, whichever template Hugo happened to insert first into
its template store wins, regardless of the user's declared suffix priority.
A second template with a *different* extension (but the same media type and
same base name) is silently discarded with the comment

> "e.g. /pages/home.foo.html and /pages/home.html where foo may be a valid
> language name in another site."

That early-return is too aggressive: it conflates the "ambiguous language
suffix" case with the "user explicitly listed multiple suffixes for one
media type" case.

## What you need to do

Make Hugo's template store, when deciding whether to keep an existing
template or replace it with a newly-inserted one, take into account the
declared suffix order of the relevant media type. Specifically:

- If two templates have the same identifier count and would otherwise
  collide, AND
- the new template's extension differs from the existing one's, AND
- both extensions are listed in the `suffixes` of the new template's
  declared media type,

then the template whose extension appears **earlier** in the `suffixes`
list must win. If the new template's extension comes earlier than the
existing one's, it replaces the existing entry. Otherwise the existing
entry stays.

The original "ambiguous language suffix" guard must still apply when none
of the above conditions hold (e.g. when the media type has only one
suffix, or when one of the two extensions isn't in the suffix list at
all). In those cases the old behaviour — keep the existing entry, drop
the new one — must be preserved.

## Acceptance criteria

A site configured with:

```toml
disableKinds = ['home','rss','section','sitemap','taxonomy','term']

[mediaTypes.'text/html']
suffixes = ['b','a','d','c']

[outputFormats.html]
mediaType = 'text/html'
```

…and four layouts `layouts/page.html.{a,b,c,d}`, each containing the
literal string `page.html.X` where `X` is the suffix, must produce the
file `public/p1/index.b` containing `page.html.b` for a single content
page `content/p1.md`.

The same priority rule must hold for arbitrary suffix lists, not just
`['b','a','d','c']` — the winner is whichever extension appears first in
the user-declared `suffixes` slice. The rule must not depend on
alphabetical order.

## Code Style Requirements

The repo's CI runs `gofmt -l` and `go vet ./...`. Your change must:

- be `gofmt`-clean (no diff produced by `gofmt -l` on touched files);
- pass `go vet ./tpl/tplimpl/...` and `go vet ./hugolib/...` without warnings;
- compile cleanly: `go build ./tpl/tplimpl/...` and `go build ./hugolib/...`
  must succeed.

Pre-existing template tests must continue to pass — in particular,
`TestOverrideInternalTemplate` in `hugolib/template_test.go` must still
pass after your change.

Follow the project's general code-style guidelines from `AGENTS.md`:
brevity, no comments stating the obvious, no exported symbols that aren't
needed outside the package, prefer existing helpers over new ones, no
debug `fmt.Print*` calls left behind.
