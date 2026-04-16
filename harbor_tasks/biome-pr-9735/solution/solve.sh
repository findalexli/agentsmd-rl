#!/bin/bash
set -e
cd /workspace/biome_repo

# Copy the fixed files from the solution volume
cp /solution/syntax_mod.rs crates/biome_markdown_parser/src/syntax/mod.rs
cp /solution/spec_test.rs crates/biome_markdown_parser/tests/spec_test.rs

# Idempotency check - look for distinctive fix line
grep -q "end.saturating_sub(start)" crates/biome_markdown_parser/src/syntax/mod.rs

echo "Fix applied successfully"