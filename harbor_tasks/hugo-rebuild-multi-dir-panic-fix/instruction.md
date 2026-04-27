# Hugo: panic during rebuild when several new directories appear together

You are working in a checkout of the Hugo static site generator
(`/workspace/hugo`, Go module `github.com/gohugoio/hugo`). A reproducible
runtime panic has been reported when Hugo's file watcher (`hugo build -w`,
or any rebuild that processes a batch of file-system events) sees a single
batch that contains BOTH:

* one or more brand-new file changes nested under some directory, AND
* two or more brand-new top-level directories at sibling locations.

## Symptom

With a fresh Hugo site whose `content/` directory is initially empty, run
`hugo build -w` in one terminal, then in another terminal run a script
that, in a single shell invocation, performs the equivalent of:

```bash
mkdir -p content/nesteddir/dir1
echo "content" >> content/nesteddir/dir1/post.md
mkdir -p content/dir1
mkdir -p content/dir2
```

The watcher delivers a single batch of path changes that includes the new
`/nesteddir/dir1/post.md` file change plus the directory pathChanges for
`/dir1`, `/dir2`, `/nesteddir`. The rebuild then crashes:

```
panic: runtime error: index out of range [1] with length 1

goroutine N [running]:
github.com/gohugoio/hugo/hugolib.(*HugoSites).fileEventsContentPaths(...)
        github.com/gohugoio/hugo/hugolib/site.go:1323
github.com/gohugoio/hugo/hugolib.(*HugoSites).processPartialFileEvents(...)
        github.com/gohugoio/hugo/hugolib/hugo_sites_build.go:1162
...
```

## What is broken

The unexported method
`(*HugoSites).fileEventsContentPaths(p []pathChange) []pathChange` in
`hugolib/site.go` is responsible for taking a batch of `pathChange`s and
suppressing every "non-dir" change that lives below any of the new
directory changes in the same batch (i.e. when a directory `D` is reported
as newly created, individual file events for files under `D/` are
redundant and must be filtered out).

The current implementation produces a slice index that exceeds the
underlying slice's length whenever the batch contains *two or more*
directory entries together with at least one file entry that is NOT under
any of those dirs. Re-running `hugo build -w` afterwards succeeds — the
panic only fires on the specific batch.

## What you must do

Repair `(*HugoSites).fileEventsContentPaths` so that, given any batch of
`pathChange` values:

1. The function NEVER panics with `index out of range`, regardless of the
   relative ordering or count of dir vs. non-dir entries.
2. The returned slice is exactly the input filtered down to:
   * every entry whose `isDir` field is true, plus
   * every non-dir entry whose `p.Path()` does NOT have any of the dir
     entries' `p.Path() + "/"` as a prefix.
3. Each non-dir entry is checked against ALL dir entries (not just the
   first one), so a change is suppressed if it is below ANY of the new
   dirs.
4. The function's exported/unexported status, signature, and the way it
   partitions input into `bundles` / `dirs` / `regular` / `others` are
   unchanged. Only the filtering loop that the panic stack points at
   needs reworking.

Do not introduce new exported identifiers in the `hugolib` package, and
do not add new helper functions for what is essentially a small filter
rewrite (the project prefers reusing existing primitives like
`strings.HasPrefix`).

## How to verify locally

The repository ships a `./check.sh` script. Invoking
`./check.sh ./hugolib/...` while iterating runs gofmt and tests on the
package; running `./check.sh` (no args) does the same across the whole
module. Your fix must keep `gofmt` and `go vet ./hugolib/` green and must
not break unrelated tests.

There is no upstream regression test in the working tree that exercises
this exact batch — you will need to reason about the loop's invariants
directly from the code in `hugolib/site.go`. The verifier will inject its
own regression tests when scoring.

## Code Style Requirements

Hugo's `AGENTS.md` (root) governs what the maintainers expect from your
edit. Notable rules that the verifier enforces:

* `gofmt` must be clean on every file you touch (this is the first step
  of `./check.sh`).
* `go vet ./hugolib/` must remain clean.
* Do NOT leave `hdebug.Printf` debug calls in committed code — CI fails
  if they are forgotten.
* Brevity: do not add comments that merely restate what the code does;
  use short variable names where context is clear.
* Never export symbols that are not needed outside the package.
* Look for existing helper functions before writing new ones.
