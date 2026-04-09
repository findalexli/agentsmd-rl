#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'FunctionLiteral(_)' crates/ty_python_semantic/src/types/call/bind.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download the PR diff and apply it
curl -sL https://github.com/astral-sh/ruff/pull/24397.diff | git apply --whitespace=fix -

echo "Patch applied successfully."

# Rebuild ty binary (incremental build — only changed crates recompiled)
CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo build --bin ty 2>&1

echo "Rebuild complete."
