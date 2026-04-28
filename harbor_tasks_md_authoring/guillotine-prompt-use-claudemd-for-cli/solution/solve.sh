#!/usr/bin/env bash
set -euo pipefail

cd /workspace/guillotine

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "src/cli/CLAUDE.md" "src/cli/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -74,7 +74,6 @@ High-performance EVM focused on correctness, minimal allocations, strong typing.
 - `primitives` - Ethereum primitives
 - `crypto` - Cryptographic functions
 - `bn254_wrapper` - BN254 curve operations
-- `guillotine-cli` - Terminal UI (src/cli/) **→ See src/cli/cli.md for ALL CLI work**
 
 ### Key EVM Components
 **Core**: evm.zig, frame.zig, stack.zig, memory.zig, dispatch.zig
@@ -135,19 +134,6 @@ pub fn add(self: *Self) Error!void {
 }
 ```
 
-## CLI Development
-
-**CRITICAL**: For ANY work in `src/cli/`, you MUST:
-1. Read and follow `src/cli/cli.md` COMPLETELY
-2. Follow the MVU pattern and package structure EXACTLY
-3. Update `src/cli/cli.md` for any architectural changes
-
-**The CLI has its own Go module** (`guillotine-cli`) with strict patterns:
-- Bubbletea MVU architecture
-- Separation of concerns (config/app/ui)
-- Pure UI functions (no state in components)
-- Single source of truth for strings/styles/keys
-
 ## EVM Opcode Navigation
 Opcodes are now organized in separate handler files:
 ```bash
diff --git a/src/cli/CLAUDE.md b/src/cli/CLAUDE.md

PATCH

echo "Gold patch applied."
