# Hugo: `--panicOnWarning` has no effect on warnings emitted during config load

The Hugo CLI exposes a `--panicOnWarning` flag whose documented behavior is
*"panic on first WARNING log"*. In the current source tree at
`/workspace/hugo`, this flag is silently ignored: passing `--panicOnWarning`
to `hugo` does **not** cause Hugo to fail when a `WARN`-level entry is
emitted during configuration loading.

## Reproducing the bug

Create a minimal site whose `module.hugoVersion` window does not include the
running Hugo version (the running `hugo` binary in this environment reports a
version above `0.148.0`):

```toml
# hugo.toml
baseURL = "https://example.org"

[module]
[module.hugoVersion]
min = "0.148.0"
max = "0.148.0"
```

…and a stub layout:

```html
<!-- layouts/all.html -->
All.
```

Build the `hugo` binary from the current source tree (`go build -o /tmp/hugo
./` from `/workspace/hugo`), then run:

```sh
/tmp/hugo --panicOnWarning
```

**Observed (broken) behaviour:** `hugo` prints the warning

```
WARN  Module "project" is not compatible with this Hugo version: ...
```

…to stderr, completes the build, and exits with status `0`.

**Expected behaviour:** because a `WARN` entry was logged and the user passed
`--panicOnWarning`, `hugo` must terminate with a **non-zero** exit status,
and the panic message — which contains the warning text **`is not compatible
with this Hugo`** — must be visible on stderr.

## Required behaviour

1. Running `hugo --panicOnWarning` in a project that produces *any*
   `WARN`-level log entry must cause `hugo` to exit with a non-zero exit
   status.
2. The compatibility-warning text **`is not compatible with this Hugo`**
   must appear on stderr (it is the message the panic-on-warning hook
   surfaces — do not swallow or rewrite it).
3. Running the same `hugo` invocation **without** `--panicOnWarning` must
   continue to succeed (exit `0`) even when warnings are produced — warnings
   alone must not become fatal.
4. Running `hugo --panicOnWarning` against a project that does *not* produce
   any warnings must still succeed (exit `0`). The flag opts in to fail-on-
   warning behaviour; on a clean build it has no effect.
5. A second hugoVersion-window assertion: a window such as `min = "9.99.0"`,
   `max = "9.99.0"` (clearly above the running build's version) must
   likewise trigger the panic when `--panicOnWarning` is set.

The fix lives in the CLI's command-wiring layer (the package that defines
the root command and the `createLogger` helper). The `loggers` package
already provides a hook value (`PanicOnWarningHook`) and the `loggers.Options`
struct already accepts a `HandlerPost` field — neither needs to be created.
The flag itself is already declared in the Hugo CLI's local-build flag set;
what is broken is how that flag's value is propagated to the logger that
gets constructed for the running command.

You should also propagate the same option through Hugo's `IntegrationTest`
helper in `hugolib/` so that integration tests written against
`IntegrationTestConfig` can opt into the same behaviour. The integration
helper builds its logger via the same `loggers.New` factory, so it needs to
forward the new option there as well.

## Out of scope

* Do **not** change the semantics of the warning itself (do not promote the
  module-compatibility warning to an error, and do not change its message).
  Other consumers of the `WARN` level still rely on it.
* Do **not** alter the public API of the `loggers` package; the necessary
  hook (`PanicOnWarningHook`) and the `HandlerPost` option are already
  exported.

## Code Style Requirements

Tests in this task invoke `gofmt` and `go vet` on the affected packages.
Before considering the task complete, the source must pass:

* `gofmt -l commands/` — must report no unformatted files.
* `go vet ./commands/...` — must exit cleanly.

Follow the repo's conventions documented in `AGENTS.md`: in particular,
prefer `qt` matchers (`b.Assert(err, qt.ErrorMatches, ...)`) over raw
`if`/`t.Fatal` checks if you add or modify Go tests, do not export
identifiers that are not needed outside the package, and avoid global state.
