#!/usr/bin/env bash
# Standardized harness test runner. Writes binary reward to /logs/verifier/reward.txt.
set -u

mkdir -p /logs/verifier

# We do NOT rebuild here. The Docker image already contains a full `pnpm
# build` (with tsc-multi) that produced both `.js` and `.mjs` outputs in
# `dist/`, which the package.json exports map relies on (e.g.
# `@openai/agents-core/_shims`). The f2p tests run TypeScript source via
# `tsx`, so they always reflect the current source state without needing
# any rebuild. The pass-to-pass vitest check imports the test target from
# `../src/runState` and only relies on the unchanged `dist/` for the
# `_shims` package alias.

cd /tests
pytest -v --tb=short test_outputs.py
status=$?

# Reward is exit code from pytest. The build step above is not part of the
# reward signal — if it failed, the imports inside test_outputs.py will error
# and surface as test failures.
if [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (Rubric judging is invoked by the harness out-of-band; do not exit early.)

exit 0
