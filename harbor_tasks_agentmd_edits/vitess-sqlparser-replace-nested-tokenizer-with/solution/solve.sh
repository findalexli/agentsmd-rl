#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitess

# Idempotent: skip if AGENTS.md already exists (added by this PR)
if [ -f go/vt/sqlparser/AGENTS.md ]; then
    echo "Patch already applied."
    exit 0
fi

MERGE=9e5141afd5c3488cb4a0aea8168b48bf198790db

git fetch origin "$MERGE" --depth=1

git checkout "$MERGE" -- \
    go/vt/sqlparser/AGENTS.md \
    go/vt/sqlparser/token.go \
    go/vt/sqlparser/comments.go \
    go/vt/sqlparser/ast_funcs_test.go \
    go/vt/sqlparser/comments_test.go \
    go/vt/sqlparser/token_test.go \
    go/vt/sqlparser/testdata/select_cases.txt

echo "Patch applied successfully."
