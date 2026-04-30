# Parallelize plugin cancellation in the host

## Symptom

When the engine asks the plugin `Host` to cancel everything in flight, the
host walks its three plugin maps in turn and calls each plugin's cancel
RPC sequentially:

* every loaded resource provider has its `SignalCancellation(ctx)` called
  one after another;
* then every analyzer has its `Cancel(ctx)` called one after another;
* then every language runtime has its `Cancel()` called one after another.

If a single plugin's cancel RPC is slow or wedged, every plugin behind it
in the iteration order never receives a cancel signal at all — most
importantly, language hosts are at the very end of the queue, and they are
exactly the processes that need to be told to shut down so any
RunPlugin-based provider they spawned can exit. The motivating bug is a
RunPlugin-based provider that does not respond to `plugin.Cancel`, which
in turn keeps the host from ever invoking `language.Cancel` to terminate
the language host that owns it.

A second, related issue: the context the host passes today to provider
and analyzer plugins is the host's long-lived request context. If a
plugin's cancel implementation is written to honour a deadline, there is
no deadline on the inbound context for it to honour, so a misbehaving
plugin can pin the cancellation goroutine indefinitely.

## Required behaviour

Rework the plugin host's cancellation entry point so that:

1. **Resource providers and analyzers are cancelled concurrently** rather
   than serially. A stuck provider must not stop another provider or any
   analyzer from receiving its cancel signal.
2. **Language runtimes are cancelled concurrently with each other**, so
   one slow language host does not delay cancellation of the others.
3. **Language runtimes are cancelled only after the resource and analyzer
   phase has finished**, because RunPlugin-based providers run inside a
   language host and should be given a chance to shut down cleanly before
   the language host that spawned them goes away.
4. **The context passed to provider and analyzer cancel calls must carry
   a deadline** so well-behaved plugins return promptly even if the
   plugin process itself is wedged. The host's own request context has no
   deadline of its own, so the deadline must be added explicitly on top
   of the cancellation invocation.
5. **All errors from the per-plugin cancel calls are still aggregated and
   returned**, so the caller sees every cancellation failure, not just
   the first.

The behaviour with no plugins, or with a single fast plugin per kind,
must remain unchanged: cancellation returns `nil` once every cancel call
has completed, and a non-nil aggregate error otherwise.

## Code Style Requirements

Per the repository's agent instructions (`CLAUDE.md` / `AGENTS.md` at the
repo root), any `.go` file change must satisfy:

* `mise exec -- make format` (gofumpt-formatted)
* `mise exec -- make lint` (golangci-lint clean)
* `mise exec -- make test_fast` (fast tests pass)

Add a changelog entry under `changelog/pending/` describing the fix; the
project's convention for these is documented in the root `CLAUDE.md`.
Newly created files should be stamped with the current year in their
copyright header.

Keep the change scoped to the cancellation rework — do not refactor or
re-style unrelated code in the same file.
