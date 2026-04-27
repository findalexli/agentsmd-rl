# Restart stopped replica IO threads after a failed Emergency Reparent Shard

You are working in a Vitess source tree at `/workspace/vitess`. The package
under change is `go/vt/vtctl/reparentutil`, which contains the
`EmergencyReparenter` (ERS) implementation.

## Background

`EmergencyReparenter.reparentShardLocked` (in
`go/vt/vtctl/reparentutil/emergency_reparenter.go`) runs a multi-step recovery
when the primary tablet of a shard goes down. Early in the operation it stops
the **IO thread** on every reachable replica (via
`StopReplicationAndGetStatus` with `IOTHREADONLY`) so that replicas can be
repointed at the new primary.

If ERS aborts before the **repoint** stage — for example, because too few
relay logs are applied within `WaitReplicasTimeout`, or because the
stop-replication step itself returned an error after stopping IO threads on
*some* replicas but not all — the function returns an error and the
replicas it touched are left with their IO threads stopped indefinitely.
Operators then have to manually run `START REPLICATION` on those tablets,
which is exactly what ERS was supposed to handle.

## Required behavior

When `reparentShardLocked` returns an error from any stage **before** ERS
begins repointing replicas at the new primary, it must restart replication
on the replicas whose IO threads were stopped *as part of this ERS
invocation*.

Concretely:

1. Track which replicas had a healthy, running IO thread *before* ERS
   stopped it. A replica should be considered "had a running IO thread" if
   the `Before` snapshot recorded by `StopReplicationAndGetStatus` shows the
   IO thread as healthy. Replicas whose IO thread was already stopped, or
   was failing to connect with a non-empty `LastIoError`, must not be
   restarted (we did not stop those, and bouncing them could mask real
   problems).

2. When the function returns successfully, no cleanup runs. Once ERS has
   passed the relay-log apply phase and is ready to repoint replicas, the
   list of replicas needing restart must be cleared — replication will be
   started by the normal flow, and we must not double-start it after the
   subsequent successful return.

3. The cleanup must use a **fresh bounded context** (do not reuse the
   parent context — it may already be cancelled when cleanup runs). Use
   `topo.RemoteOperationTimeout` as the bound. Detach from any cancellation
   on the parent.

4. The cleanup must verify it still holds the shard lock before calling
   any tablet-manager RPCs. If the lock has been lost, log a warning that
   identifies the keyspace/shard and skip the restart — do not attempt
   RPCs without the lock.

5. Restart calls should run concurrently across replicas (a slow tablet
   must not block the others). Errors from individual restarts must be
   collected and surfaced — wrap them into the original error using `%w`
   so the caller still sees the underlying ERS failure, and append the
   cleanup failure detail.

6. The semi-sync flag passed to `StartReplication` must be derived from
   the **previous primary** and the durability policy in effect for the
   ERS run. If the previous primary is unknown (nil), pass `false` for
   semi-sync.

7. Log every cleanup action: how many replicas are being restarted, and a
   per-replica log line that includes the tablet alias formatted via
   `topoproto.TabletAliasString`.

## Surfacing partial snapshots

`stopReplicationAndBuildStatusMaps` (in
`go/vt/vtctl/reparentutil/replication.go`) currently returns `nil` for the
snapshot whenever it cannot revoke writes from enough tablets to guarantee
safety. That throws away the information about which replicas already had
their IO thread stopped, making the cleanup above impossible. The caller
must be able to see those stopped replicas even when the overall stop step
fails. Adjust the function so that the partial snapshot is returned to the
caller in this branch (the error itself is already returned and remains
unchanged).

## What must work

The cleanup must correctly handle these scenarios:

* **Partial stop failure.** ERS calls `StopReplicationAndGetStatus` on the
  primary plus three replicas. The primary call fails, two of the replica
  calls succeed (one had `IoState=Running`, the other had
  `IoState=Connecting` with empty `LastIoError`), and the third replica
  call fails. ERS must return an error containing
  `"failed to stop replication and build status maps"` and must call
  `StartReplication` exactly once per **successfully-stopped** replica — and
  not on the failed-call replica (we never stopped it) or on the primary
  (which is dead).

* **Relay log apply timeout.** ERS successfully stops one replica whose IO
  thread was running and one whose IO thread was already stopped before
  ERS started. The relay-log apply step then exceeds `WaitReplicasTimeout`
  on the stopped-by-ERS replica. ERS must return an error containing
  `"could not apply all relay logs within the provided waitReplicasTimeout"`
  and must call `StartReplication` only on the replica whose IO thread *it*
  stopped — not on the replica that was already stopped before ERS ran.

* **Partial revoke.** When `stopReplicationAndBuildStatusMaps` cannot
  revoke writes from enough tablets, the partial snapshot (the
  `replicationSnapshot` accumulated so far) is returned to the caller
  alongside the error.

## Code Style Requirements

This package follows Vitess conventions documented in `CLAUDE.md`:

- Run `gofumpt -w` and `goimports -local "vitess.io/vitess" -w` on every
  Go file you change. The CI gate in `go vet ./go/vt/vtctl/reparentutil/...`
  must pass.
- Prefer `vterrors.Errorf`/`vterrors.Wrapf` (with the appropriate
  `vtrpcpb.Code`) over the stdlib `fmt.Errorf` and `errors` package for
  new error returns. Wrapping with `%w` to preserve an existing error
  chain across cleanup boundaries is acceptable.
- Format `*topodatapb.TabletAlias` values for log/error messages with
  `topoproto.TabletAliasString(alias)`.
- Preallocate result slices when the upper bound is known
  (`make([]T, 0, len(source))`).
- New helpers used only inside the package should stay unexported.
