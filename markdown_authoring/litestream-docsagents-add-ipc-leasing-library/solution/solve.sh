#!/usr/bin/env bash
set -euo pipefail

cd /workspace/litestream

# Idempotency guard
if grep -qF "- **`$PID` config expansion**: Config files support `$PID` to expand to the curr" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -16,14 +16,20 @@ Litestream is a disaster recovery tool for SQLite that runs as a background proc
 - **Use `litestream ltx`**: Not `litestream wal` (deprecated)
 - **Use `litestream reset`**: Clears corrupted local LTX state for a database. See `cmd/litestream/reset.go`
 - **`auto-recover` config**: Replica option that automatically resets local state on LTX errors. Disabled by default. See `replica.go`
+- **Retention enabled by default**: `Store.RetentionEnabled` is `true` by default. Disable only when cloud lifecycle policies handle cleanup. See `store.go`
+- **IPC socket disabled by default**: Control socket is off by default. Enable with `socket.enabled: true` in config. See `server.go`
+- **`$PID` config expansion**: Config files support `$PID` to expand to the current process ID, plus standard `$ENV_VAR` expansion. See `cmd/litestream/main.go`
+- **`litestream ltx -level`**: Use `-level 0`–`9` or `-level all` to inspect specific compaction levels. See `cmd/litestream/ltx.go`
 
 ## Layer Boundaries
 
 | Layer | File | Responsibility |
 |-------|------|----------------|
-| DB | `db.go` | Database state, restoration, WAL monitoring |
+| DB | `db.go` | Database state, restoration, WAL monitoring, library API (`SyncStatus`, `SyncAndWait`, `EnsureExists`) |
 | Replica | `replica.go` | Replication mechanics only |
-| Storage | `**/replica_client.go` | Backend implementations |
+| Storage | `**/replica_client.go` | Backend implementations (includes `ReplicaClientV3` for v0.3.x restore) |
+| IPC | `server.go` | Unix socket control API (register/unregister, /txid, pprof) |
+| Leasing | `leaser.go`, `s3/leaser.go` | Distributed lease acquisition via conditional writes |
 
 Database state logic belongs in DB layer, not Replica layer.
 
@@ -52,6 +58,7 @@ pre-commit run --all-files
 | [docs/LTX_FORMAT.md](docs/LTX_FORMAT.md) | Replication format |
 | [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) | Test strategies |
 | [docs/REPLICA_CLIENT_GUIDE.md](docs/REPLICA_CLIENT_GUIDE.md) | Adding storage backends |
+| [docs/PROVIDER_COMPATIBILITY.md](docs/PROVIDER_COMPATIBILITY.md) | Provider-specific S3/cloud configs |
 
 ## Checklist
 
PATCH

echo "Gold patch applied."
