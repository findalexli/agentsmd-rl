#!/bin/bash
set -e

cd /workspace/biome

echo "=== Before patch ==="
git status

# Apply the gold patch
curl -sL "https://github.com/biomejs/biome/pull/9782.patch" | git apply -v

echo "=== After patch ==="
git status
git diff --stat

# Verify the distinctive line is present (idempotency check)
if grep -q "force_relex_at_line_start" crates/biome_markdown_parser/src/parser.rs; then
    echo "PATCH APPLIED OK"
else
    echo "ERROR: force_relex_at_line_start not found after patch"
    exit 1
fi