# `pulumi refresh --preview-only` should not lock the state file (diy backend)

## Background

This repository (`pulumi/pulumi`) ships several backends used by the CLI to
persist stack state. The "diy" backend (`pkg/backend/diy/`) writes state to
a blob store (local filesystem, S3, GCS, …) and uses a small JSON file at
`.pulumi/locks/<stack>/<lockID>.json` to coordinate concurrent updates.
The package-private `Lock` / `Unlock` / `checkForLock` methods live in
`pkg/backend/diy/lock.go`.

Mutating CLI verbs such as `up`, `import`, `destroy`, `refresh`, and stack
rename all call `b.Lock(ctx, stack.Ref())` before doing real work, so that
two `pulumi` processes acting on the same stack concurrently can detect
the conflict and bail out cleanly.

## Symptom

`pulumi refresh` accepts a `--preview-only` flag (added in
[pulumi/pulumi#1666](https://github.com/pulumi/pulumi/issues/1666)) which
asks the engine to compute the refresh plan without writing it back. With
this flag set, no state file is mutated.

For the diy backend, however, `Refresh` still acquires (and on exit
releases) the stack lock when called with `PreviewOnly=true`. That has
two visible consequences:

1. A user running `pulumi refresh --preview-only` against a stack that is
   already locked by another in-flight operation (perhaps a long-running
   `pulumi up` on a teammate's machine, or a stale lock left behind by a
   killed process) cannot inspect refresh output without first cancelling
   the lock. The error surfaced is:

   ```
   the stack is currently locked by N lock(s). Either wait for the other
   process(es) to end or delete the lock file with `pulumi cancel`.
   ```

2. Two concurrent `--preview-only` refreshes against the same stack are
   rejected, even though neither writes to the state file.

This is inconsistent with the equivalent code path for `pulumi preview`,
which deliberately skips locking for the same reason
([pulumi/pulumi#8642](https://github.com/pulumi/pulumi/pull/8642)). Issue
[pulumi/pulumi#22384](https://github.com/pulumi/pulumi/issues/22384)
tracks the inconsistency.

## Expected behaviour

For the diy backend's `Refresh` implementation:

- When the operation is `PreviewOnly=true`, `Refresh` must NOT call
  `b.Lock` / `b.Unlock`. The function should not return any
  "currently locked" error originating from the lock-conflict check, even
  if a foreign lock is currently held by another backend instance for the
  same stack.
- When the operation is `PreviewOnly=false` (the default), `Refresh` must
  continue to acquire and release the lock exactly as before. A foreign
  lock held during a non-preview refresh must still cause the call to
  fail with the existing "currently locked" error from
  `checkForLock`. Removing locking for the non-preview path would be a
  regression.

In both branches, all other observable behaviour (error propagation,
`PreviewThenPromptThenExecute` for the non-preview path, the
`b.apply`-based fast path for the preview path, and the `defer
b.Unlock` cleanup when locking does occur) must be preserved.

## Where to look

The relevant function is `Refresh` on `*diyBackend`, defined in
`pkg/backend/diy/backend.go`. The lock helpers it uses (`Lock`, `Unlock`,
`checkForLock`) live in `pkg/backend/diy/lock.go` and should not need
to change.

You do NOT need to modify any other backend — only the diy implementation
is affected by this issue.

## Constraints

- This repository follows the conventions documented in `AGENTS.md` and
  `pkg/AGENTS.md` at the repository root and under `pkg/`. Read them
  before making changes.
- Do not refactor or "clean up" unrelated code. Make the smallest change
  that fixes the symptom.
- Do not weaken the locking guarantee for the non-preview-only path.
- Adding an entry under `changelog/pending/` is conventional for
  user-visible fixes but is not required for the automated tests to
  pass.

## How your change will be verified

The grader runs `go test` on `pkg/backend/diy/...`. The two harness
tests that drive this exercise call `Refresh` from one backend instance
while a second instance (with a different lockID) holds the stack lock,
and assert on whether the resulting error mentions `"currently locked"`.
The full diy backend test suite must continue to pass. `go vet
./backend/diy/...` must remain clean.

## Code Style Requirements

The verifier runs `go vet ./backend/diy/...`. Any source-level issue it
detects (printf format strings, unreachable code, struct-tag mistakes,
etc.) will fail the task.

The repository's CI also enforces `gofumpt` formatting and uses
`golangci-lint` (see `AGENTS.md` for the canonical commands). Keep the
diff `gofmt`/`gofumpt`-clean — no stray whitespace, tabs vs spaces, or
import-grouping changes.
