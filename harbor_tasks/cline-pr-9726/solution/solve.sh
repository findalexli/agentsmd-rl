#!/bin/bash
set -e
cd /workspace/cline

git fetch --filter=blob:none origin bce71b4448815975d9192d60432b694ddcd5fa03
git checkout bce71b4448815975d9192d60432b694ddcd5fa03

grep -q "findMostRecentTaskForWorkspace" cli/src/index.ts && echo "Idempotency check passed"
