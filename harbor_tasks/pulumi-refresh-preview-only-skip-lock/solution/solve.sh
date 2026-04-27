#!/usr/bin/env bash
# Gold solution for pulumi/pulumi#22385:
#   "Remove state lock for refresh --preview-only for diy backend"
#
# The patch is applied from /solution/fix.patch — a local file checked
# into this task. solve.sh does NOT fetch the gold from any external
# source (the rubric forbids `gh pr diff`, `curl …github.com…`,
# `git show <merge>`, etc.). Idempotent: running twice is a no-op.

set -euo pipefail

REPO=/workspace/pulumi
TARGET="$REPO/pkg/backend/diy/backend.go"
PATCH=/solution/fix.patch

cd "$REPO"

# Idempotency probe: when the fix is in place, the first non-comment
# statement of Refresh is `if op.Opts.PreviewOnly`, NOT `err := b.Lock`.
if awk '
  /^func \(b \*diyBackend\) Refresh\(ctx context\.Context, stack backend\.Stack,/ {found=1; next}
  found && /^\tif op\.Opts\.PreviewOnly \{/ {print "applied"; exit}
  found && /^\terr := b\.Lock\(ctx, stack\.Ref\(\)\)/ {print "unapplied"; exit}
' "$TARGET" | grep -q '^applied$'; then
    echo "solve.sh: patch already applied — exiting idempotently."
    exit 0
fi

git apply "$PATCH"
echo "solve.sh: patch applied from $PATCH"
