#!/bin/bash
set -e

cd /workspace/mantine

# Get the actual diff from the repository and apply it
git diff 4e071c14d8febd7e583ef59a9f8eb9245c22a3ae..67dc866fa74d6301fa02f02cfd0212ffddf0c728 -- packages/@mantine/mcp-server/src/server.ts > /tmp/gold.patch
git apply /tmp/gold.patch

# Idempotency check - look for distinctive line from the patch
grep -q "readline.createInterface" packages/@mantine/mcp-server/src/server.ts
