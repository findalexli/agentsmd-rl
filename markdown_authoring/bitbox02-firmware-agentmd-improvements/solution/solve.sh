#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bitbox02-firmware

# Idempotency guard
if grep -qF "Any shell command can be run inside docker using `./scripts/docker_exec.sh <comm" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -23,6 +23,9 @@ wrapper in the bitbox02 crate.
 - `make dockerpull` / `make dockerdev`: fetch and enter the maintained development container.
 
 All make commands are to be run inside docker like this: `./scripts/docker_exec.sh make -j <command>`, e.g.  `./scripts/docker_exec.sh make -j firmware`.
+Any shell command can be run inside docker using `./scripts/docker_exec.sh <command>` - do not use
+`bash -lc` before the command.
+
 
 - `make firmware` / `make bootloader`: compile firmware or bootloader ELFs into `build/`.
 - `make simulator`: build the Linux simulator under `build-build-noasan/bin/`.
@@ -38,6 +41,7 @@ pinned toolchain in `rust-toolchain.toml`; keep module paths aligned with `src/r
 bindings (`cbindgen`, protobuf) when interfaces change.
 
 For C code changes, run ./scripts/format to format the code. For Python changes, run `black` to format the code.
+For Rust code changes, run `cd src/rust && cargo fmt` to format the code.
 
 ## Testing Guidelines
 Place new C specs in `test/unit-test` and add doubles to `test/hardware-fakes` when hardware
PATCH

echo "Gold patch applied."
