#!/usr/bin/env bash
set -euo pipefail

cd /workspace/erigon

# Idempotency guard
if grep -qF "description: Build the Erigon binary using make. Use this when you need to compi" ".claude/skills/erigon-build/SKILL.md" && grep -qF "description: Run the Erigon segment retire command to build, merge, and clean sn" ".claude/skills/erigon-seg-retire/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/erigon-build/SKILL.md b/.claude/skills/erigon-build/SKILL.md
@@ -0,0 +1,42 @@
+---
+name: erigon-build
+description: Build the Erigon binary using make. Use this when you need to compile erigon before running any erigon commands.
+allowed-tools: Bash
+---
+
+# Build Erigon Binary
+
+Build the Erigon binary by running `make erigon` from the repository root.
+
+## Build Command
+
+```bash
+make erigon
+```
+
+This compiles the Erigon binary and places it at `./build/bin/erigon`.
+
+## What the Build Does
+
+- Compiles the main Erigon executable
+- Sets version information from git (commit, branch, tag)
+- Applies appropriate CGO flags for the platform
+- Outputs binary to `build/bin/erigon`
+
+## Prerequisites
+
+- Go (version specified in go.mod)
+- C compiler (gcc or clang)
+- Make
+
+## After Building
+
+The binary will be available at:
+```
+./build/bin/erigon
+```
+
+You can verify the build by running:
+```bash
+./build/bin/erigon --version
+```
diff --git a/.claude/skills/erigon-seg-retire/SKILL.md b/.claude/skills/erigon-seg-retire/SKILL.md
@@ -0,0 +1,64 @@
+---
+name: erigon-seg-retire
+description: Run the Erigon segment retire command to build, merge, and clean snapshot files. Use this for snapshot publication readiness preparation.
+allowed-tools: Bash, Read
+---
+
+# Erigon Segment Retire Command
+
+The `erigon seg retire` command prepares snapshot files for publication by performing build, merge, and cleanup operations on segment files.
+
+## Prerequisites
+
+1. **Erigon must be stopped** - The command requires exclusive access to the datadir
+2. **Binary must be built** - Run `/erigon-build` first if the binary doesn't exist
+3. **Datadir must exist** - A synced Erigon datadir with blockchain data
+
+## Command
+
+```bash
+./build/bin/erigon seg retire --datadir=<path>
+```
+
+Replace `<path>` with the actual path to your Erigon data directory.
+
+## What the Command Does
+
+The retire command performs these operations in sequence:
+
+1. **Build Missing Indices** - Creates any missing indices for block and Caplin snapshots
+2. **Retire Blocks** - Freezes blocks from the database into snapshot files
+3. **Remove Overlaps** - Cleans up overlapping snapshot files
+4. **Prune Ancient Blocks** - Removes block data from the database that has been successfully snapshotted
+5. **Build State History** - Creates missing accessors and builds state history snapshot files
+6. **Prune State History** - Removes state history that has been snapshotted
+7. **Merge and Cleanup** - Merges smaller snapshot files into larger ones and removes overlaps
+
+## Usage in Snapshot Release Workflow
+
+This command is part of the "Publishable v2" snapshot release flow:
+
+1. Shutdown Erigon
+2. **Run `seg retire`** (this command)
+3. Optionally run `seg clearIndexing`
+4. Run `seg index`
+5. Create torrent files
+6. Run integrity check
+7. Run `publishable` command
+
+## Example
+
+```bash
+# Build the binary first (if needed)
+make erigon
+
+# Ensure Erigon is stopped, then run seg retire
+./build/bin/erigon seg retire --datadir=/data/erigon
+```
+
+## Important Notes
+
+- **File Lock**: If Erigon is running, the command will fail due to file lock
+- **Long running**: This command can take significant time on mainnet
+- **Disk I/O intensive**: Performs extensive read/write operations
+- **Resource intensive**: Designed to maximize resource utilization
PATCH

echo "Gold patch applied."
