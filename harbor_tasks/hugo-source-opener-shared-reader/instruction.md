# Fix shared reader in `Source.ValueAsOpenReadSeekCloser`

The Hugo source tree is at `/workspace/hugo`, checked out at base commit
`b55d452e46e81369a65978459a0683efa484c11b`.

## The bug

The package `github.com/gohugoio/hugo/resources/page/pagemeta` exposes a type
`Source`. On `Source` there is a method:

```go
func (s Source) ValueAsOpenReadSeekCloser() hugio.OpenReadSeekCloser
```

`hugio.OpenReadSeekCloser` is `func() (hugio.ReadSeekCloser, error)` — i.e.
calling it should "open" a reader. Callers may invoke the returned opener
**multiple times** and hold several of the resulting readers **concurrently**.

The current implementation does not provide that guarantee. Every call to the
opener returns the **same shared** underlying reader, with its position simply
seeked back to 0. As a result, when two readers from the same opener are
held concurrently, advancing one (by reading from it) silently advances —
or rewinds — the other.

The expected contract is: each call to the opener returns an **independent**
`ReadSeekCloser` whose read position is unaffected by reads or seeks on any
reader returned by an earlier call.

## Concrete symptom

With `s := pagemeta.Source{Value: "abcdefgh"}` and
`opener := s.ValueAsOpenReadSeekCloser()`:

1. Open `r1`, read 4 bytes from it. Got: `"abcd"`. Position: 4.
2. Open `r2`. Read all of `r2`. Got: `"abcdefgh"`. Position of `r2`: 8.
3. Read the rest of `r1`.
   - **Expected:** `"efgh"` (the four bytes after `r1`'s position 4).
   - **Actual:** an empty string, because `r1` and `r2` are the same reader
     and step 2 left the shared position at 8.

The same problem must not occur when the source value is a `[]byte`
(e.g. `[]byte("0123456789")`) or another type cast to string by the
existing `ValueAsString()` helper. Three or more independent readers held
simultaneously must each see the full content from the start, regardless of
read activity on the others. For instance, with content
`"the quick brown fox jumps over the lazy dog"` and three readers open at
once, interleaving reads across them must not disturb independent positions:
reading 10 bytes from the first, fully consuming the second and third, then
reading the remainder of the first must yield the expected tail.

This bug breaks downstream callers that pass the returned opener to image
processing (e.g. `Resize`) when the same source value is also being read
elsewhere — e.g. an `AddResource` call that uses `pixel.Content` (a string)
as the value. The image processor tries to re-open the reader after another
consumer has already moved its position, and reads zero bytes instead of
the image data.

## Your task

Modify `Source.ValueAsOpenReadSeekCloser()` so that each invocation of the
returned opener yields a reader whose position is independent of any
previously-returned reader.

Reuse existing helpers in `github.com/gohugoio/hugo/common/hugio` rather than
introducing a new wrapper type or new exported symbols. Do not export any
new top-level symbols from the `pagemeta` package as part of the fix.

## Code Style Requirements

The repository's `./check.sh` script (and the harness's automated checks)
enforce all of the following on the affected package
`./resources/page/pagemeta/`:

- **`gofmt`** — every changed `.go` file must be `gofmt`-clean.
- **`go vet`** — must report no issues.
- **`staticcheck`** (honnef.co/go/tools) — must report no issues.
- **`go test`** — all existing tests in the package must continue to pass.
- **`go build .`** — the top-level `hugo` binary must still build.

Project-wide guidance from `AGENTS.md` (apply to anything you add):

- Brevity is good. Keep the fix and any new tests minimal.
- Don't use comments to explain the obvious.
- Don't introduce global state.
- In tests, use the `qt` matcher style (`c.Assert(x, qt.Equals, y)`) used
  elsewhere in the package, not raw `if`/`t.Fatal`.
- Never export symbols not needed outside the package.
- If you add temporary debug prints, remove them before finishing.
