# Fix auto-creation of root sections in multilingual Hugo sites

You are working in a checkout of [Hugo](https://github.com/gohugoio/hugo)
at `/workspace/hugo`. There is a bug in how root section pages are
auto-created for multilingual sites; your job is to fix it.

## The bug

Hugo lets you keep per-language content in sibling directories
(`content/<lang>/...`) by configuring `contentDir` per language. When a
section directory (e.g. `s1/`) contains content files in **multiple**
languages but **no** `_index.md` in any of them, Hugo is supposed to
auto-create a section page (`s1`) for **every language** that owns at
least one content file under that section.

Today it does not. With the following minimal multilingual site:

```toml
# hugo.toml
disableKinds = ['rss','sitemap','taxonomy','term']
defaultContentLanguage = "fr"
defaultContentLanguageInSubdir = true

[languages.fr]
contentDir = "content/fr"
weight = 1
[languages.en]
contentDir = "content/en"
weight = 2
[languages.de]
contentDir = "content/de"
weight = 3
```

…and these content files (no `_index.md` anywhere):

```
content/de/s1/p1.md   (front matter: title: p1)
content/en/s1/p2.md   (front matter: title: p2)
content/fr/s1/p3.md   (front matter: title: p3)
```

…and these layouts:

```
layouts/home.html        ->  HOME {{ .Language.Name }}
layouts/page.html        ->  {{ .Title }} {{ .Language.Name }}
layouts/section.html     ->  {{ .Title }} {{ .Language.Name }}
```

…running `hugo` should produce a section page for `s1` in **all three**
languages:

| Path                          | Expected body |
|-------------------------------|---------------|
| `public/de/s1/index.html`     | `s1 de`       |
| `public/en/s1/index.html`     | `s1 en`       |
| `public/fr/s1/index.html`     | `s1 fr`       |

Currently, only one of the three section pages exists; the other two are
missing entirely (`open ...index.html: file does not exist`). The
per-language `home` and `page` outputs are unaffected — those still
render correctly. The corresponding leaf pages
(`public/<lang>/s1/<pN>/index.html`) also render correctly. Only the
auto-created **section** pages are missing.

## What we want

After your fix:

* For every language that owns at least one descendant content file under
  a root section (and where no explicit `_index.md` defines that section),
  Hugo must auto-create a section page for that language.
* Behavior for sites where `_index.md` *is* present, for taxonomies, and
  for sections owned by a single language must be unchanged.
* Existing behavior for terms, taxonomies, RSS, and sitemap remains
  governed by `disableKinds` / explicit configuration — you are only
  fixing the auto-creation path inside the page assembler.

The fix lives in the `hugolib` package's page-assembly machinery; this
is where Hugo decides, while walking the content tree, whether to
synthesize a section node and which language vectors to attach it to.
You do not need to add or modify any test files — the verifier supplies
its own integration test that exercises the multilingual scenario above
and asserts on the three `public/<lang>/s1/index.html` files.

## How to iterate

* The repository's own checks are wired up via `./check.sh
  ./hugolib/...` — use it while iterating on a single package, and
  `./check.sh` when you think you are done. It runs `gofmt`,
  `staticcheck`, and the Go tests.
* If you need ad-hoc debug printing, use `hdebug.Printf` rather than
  `fmt.Println` (CI fails the build if any debug-print helpers are left
  behind in the merged code).

## Code Style Requirements

The verifier runs `gofmt -l hugolib` and fails on any output, so all
files you touch must be `gofmt`-clean. Beyond that, the project's
`AGENTS.md` expects:

* Brevity in code, comments, and commit messages.
* Self-explanatory names; no comments that just restate the obvious.
* Do not export new symbols that aren't needed outside their package.
* Avoid global state.
* Search for existing helpers before introducing new ones — this is a
  large, mature codebase and many primitives (path parsing, content-tree
  walking, language-vector handling, post-walk hooks) already exist.
