# Fix deadlock when cancelling a Pulumi operation

You are working in a checkout of [`pulumi/pulumi`](https://github.com/pulumi/pulumi)
at a base commit that contains a deadlock in the CLI's progress display.

## Symptom

When a user presses **Ctrl+C** during a `pulumi up` / `preview` / `destroy`
running in a terminal that uses the **message renderer** (rather than the
tree renderer — e.g. on Windows, or any terminal that can't be put into raw
mode), the CLI hangs indefinitely instead of cancelling.

The cause is a goroutine deadlock in the progress display's handling of
**system events**. A system event is the engine event the CLI emits for
out-of-band messages such as `^C received; cancelling.`

You can reproduce the deadlock with the following minimal scenario, which
should complete promptly but currently hangs forever:

1. Start `ShowProgressEvents` with a non-raw mock terminal (the same
   shape produced by `terminal.NewMockTerminal(out, 80, 24, false)`),
   which selects the message renderer.
2. Send one `engine.StdoutEventPayload` (a system event — the same kind
   of event the engine produces for `^C received; cancelling.`) on the
   event channel.
3. Send `engine.NewCancelEvent()` and close the channel.
4. Wait on `doneChannel`.

On the buggy code, the goroutine running the display never closes
`doneChannel` — it is blocked. On a correct fix, `doneChannel` closes
within a fraction of a second.

## What is broken

The deadlock is between two locks on the same `sync.RWMutex` held by the
`ProgressDisplay`:

- The system-event handler calls `eventMutex.Lock()` (acquiring the
  **write** lock on the display's event mutex) while it appends to
  internal state and then asks the renderer to draw the message.
- The message renderer's draw path eventually calls back into a method
  on the display that takes the **read** lock on that same event mutex.

Because the handler defers `display.eventMutex.Unlock()` at the top of
the function, the write lock is still held when
`display.renderer.systemMessage(payload)` is called, which — for the
message renderer — eventually acquires the read lock. Go's
`sync.RWMutex` does not allow a goroutine that holds the write lock
to also acquire the read lock (and pending readers can block once a
writer is queued), so the second acquisition deadlocks.

History: this regression was introduced in PR #17019 and partially
fixed in PR #19434, which addressed the equivalent case for
`handleProgressEvent` but missed the system-event case.

## What "fixed" means

A solution is correct when:

- Sending a system event into `ShowProgressEvents` running with a
  non-raw mock terminal completes promptly (the done channel closes,
  no deadlock).
- The existing `pkg/backend/display` tests still pass.
- The fix is minimal and does not introduce new abstractions or
  refactor unrelated code.

## Where to look

The deadlock lives in the CLI's display backend, in the function that
handles system events on the `ProgressDisplay`. Search for the system
event handler on `ProgressDisplay`. The relevant call into the renderer
is `display.renderer.systemMessage(payload)`.

You do **not** need to change the renderer interface, the
`messageRenderer` implementation, or the tree renderer.

## Code Style Requirements

- Repo uses Go 1.25. Run `go build ./backend/display/...` from `pkg/`
  to confirm your change compiles cleanly.
- Per the repo's `CLAUDE.md`: any change to a `.go` file should be
  followed by `make format`, `make lint`, and `make test_fast`. Even
  if you don't run them, your code should pass `gofumpt` and standard
  `go vet`. Do not leave unused imports or unused variables.
- Per the repo's `pkg/AGENTS.md`: changes under `pkg/backend/display/`
  should come with a test that exercises display behaviour through
  pre-constructed engine events. The harness already includes a
  regression test for the deadlock, but a behavioural test of your own
  alongside the fix is encouraged.
- Per the repo's `CLAUDE.md`: most PRs require a changelog entry under
  `changelog/pending/`. For a user-visible CLI fix, a YAML entry with
  `type: fix` and `scope: cli/display` is expected.
- Keep the change minimal. The repo explicitly forbids "sweeping
  changes, refactors of unrelated code, or unnecessary abstractions".

## Working tree

The repo is checked out at `/workspace/pulumi`. The `pkg/` Go module
is the one you'll edit; `sdk/` is referenced via a local `replace`
directive in `pkg/go.mod`.
