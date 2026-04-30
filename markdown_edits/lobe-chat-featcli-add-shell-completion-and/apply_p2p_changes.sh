#!/usr/bin/env bash
# Script to apply p2p enrichment changes
# Must be run as the user who owns the task files (user:1001)

set -e

cd /workspace/task

echo "Applying p2p enrichment changes..."

# Backup original files
cp tests/test_outputs.py tests/test_outputs.py.bak
cp eval_manifest.yaml eval_manifest.yaml.bak

# Apply new files
cp test_outputs_updated.py tests/test_outputs.py
cp eval_manifest_updated.yaml eval_manifest.yaml

echo "Changes applied successfully!"
echo ""
echo "Summary of changes:"
echo "- Added 3 new pass_to_pass tests with origin: repo_tests"
echo "  - test_repo_typecheck: Runs 'npx tsc --noEmit'"
echo "  - test_repo_unit_tests: Runs vitest on agent, bot, and auth tests"
echo "  - test_repo_build: Runs 'bun run build'"
echo ""
echo "Next steps:"
echo "1. Fix the Dockerfile to install from workspace root:"
echo "   Change: WORKDIR /workspace/lobe-chat/apps/cli"
echo "   To:     WORKDIR /workspace/lobe-chat"
echo "   Then:   RUN bun install --frozen-lockfile || bun install"
echo "   Then:   WORKDIR /workspace/lobe-chat/apps/cli"
echo ""
echo "2. Build the Docker image:"
echo "   cd /workspace/task/environment && docker build -t task-env ."
echo ""
echo "3. Run the tests to verify:"
echo "   rm -f /logs/verifier/reward.txt"
echo "   docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh"
echo "   cat /logs/verifier/reward.txt"
