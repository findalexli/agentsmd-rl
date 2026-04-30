# Tar.Sync stat-error misclassification

You are working in the [docker/compose](https://github.com/docker/compose)
repository, checked out at a base commit located at
`/workspace/compose`. The package under
`internal/sync` is responsible for syncing host paths into running
containers via a streamed tar archive.

## The bug

`(*Tar).Sync(ctx, service, paths)` decides, for each `PathMapping`,
whether the host path should be **copied** into the container or whether
its container counterpart should be **deleted**. The decision is driven
by `os.Stat(p.HostPath)`:

- if the path **exists** → it should be added to the copy list,
- if the path **does not exist** (`fs.ErrNotExist`) → its container
  counterpart should be added to the delete list,
- if `os.Stat` fails for **any other reason** (e.g. `EACCES` on a parent
  directory, `EIO`, `ENOTDIR`) → the function should **return that error
  immediately**, wrapping it with the offending host path so the caller
  can see the original cause.

The current implementation collapses this into a two-way branch and
silently treats every non-`ErrNotExist` stat failure as if the path
existed and was copyable. This masks real errors and produces cryptic
downstream failures (e.g. the path silently disappears from the next
sync but no error is ever surfaced).

## What "fixed" looks like

After your fix, the following observable behaviors must hold for
`(*Tar).Sync(ctx, service, paths)` (where `paths` is a slice of
`*PathMapping`):

1. Every `*PathMapping` whose `HostPath` exists is appended to the copy
   list (`Untar` is invoked once per matching container, no `rm -rf`
   command is issued for that path).
2. Every `*PathMapping` whose `HostPath` does not exist
   (`errors.Is(err, fs.ErrNotExist)`) results in a
   `["rm", "-rf", <ContainerPath>]` exec command being issued and no
   `Untar` for that path.
3. If `os.Stat(p.HostPath)` returns an error that is **not**
   `fs.ErrNotExist`, the function returns a non-nil error **before**
   touching any container. The returned error must:
   - contain the substring `permission denied` when the underlying
     syscall error is `EACCES` (i.e. the original error must be
     preserved through the wrapper, so `errors.Is(err,
     fs.ErrPermission)` and a textual match against `permission denied`
     both succeed),
   - contain the offending host path so the caller can identify which
     mapping failed.
4. When `Sync` returns such a stat error, no copy and no delete must be
   attempted: `Untar` is not called and no exec command (`rm -rf` or
   otherwise) is issued.
5. Within a single call mixing existing + non-existing host paths, the
   existing path is still copied and the missing path still issues a
   single `rm -rf` exec command whose final argument contains the
   missing entry's `ContainerPath` basename. The two cases must remain
   independently classified.

The follow-on file the sibling unit-test pattern uses (`entriesForPath`
in the same package) is a good reference for the three-way error
classification you should adopt.

## Reproducing the symptom

Construct, on a non-root account, a directory tree like:

    /tmp/X/                     (mode 0700, owned by you)
    /tmp/X/secret.txt           (regular file)

then `chmod 0000 /tmp/X`. A subsequent `os.Stat("/tmp/X/secret.txt")`
returns `EACCES` (`*fs.PathError{Err: syscall.EACCES}`), which
`errors.Is(err, fs.ErrNotExist)` evaluates to `false`. The buggy
`Sync()` falls through and adds the path to the copy list, returning
`nil`; the fixed `Sync()` returns an error whose message contains
`permission denied` and the offending path.

## Constraints

- Do **not** change the public surface of the `sync` package
  (`(*Tar).Sync` signature, the `Syncer` interface, etc.).
- Preserve the existing behavior for the `err == nil` and
  `fs.ErrNotExist` branches.
- The fix must compile under Go 1.25 with the existing imports already
  declared in the file (you may already use `fmt`, `errors`, `io/fs`,
  `os` from the existing import block).
- The error you return for case 3 must wrap the original `os.Stat`
  error with `%w` (not `%v`) — the caller relies on the error chain to
  recover the underlying syscall error.

## Code Style Requirements

This repository's automated test suite invokes the following tooling on
your patch — your fix must pass all of them with no findings:

- `go build ./internal/sync/...` — must compile cleanly.
- `go vet ./internal/sync/...` — must report zero issues.
- `golangci-lint run ./internal/sync/...` — the repo uses
  **golangci-lint v2** (configuration in `.golangci.yml`). Relevant
  rules that the test suite checks against include:
  - `errorlint`: wrap errors with `%w`, not `%v`.
  - `gocyclo` (max complexity 16) and `lll` (max line length 200).
  - `depguard` / `gomodguard`: do **not** introduce imports of
    `io/ioutil`, `github.com/pkg/errors`, `gopkg.in/yaml.v2`,
    `golang.org/x/exp/maps`, `golang.org/x/exp/slices`,
    `github.com/docker/docker/errdefs`,
    `github.com/stretchr/testify/{assert,require,suite}`. Use stdlib
    `errors`/`fmt`, the stdlib `slices`/`maps` packages, and
    `gotest.tools/v3` for assertions in tests.
  - `forbidigo`: in test files, use `t.Context()` rather than
    `context.Background()` or `context.TODO()`.
- Formatting is enforced by `gofumpt` and `gci` (stdlib first, then
  third-party, then local module).

These rules are pulled directly from the repository's `CLAUDE.md` and
`.golangci.yml`; the harness will fail your submission if the linter
emits findings, even if the behavioral tests pass.
