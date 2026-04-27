#!/bin/bash
set -euo pipefail

cd /workspace/effect

# Idempotency guard -- distinctive line introduced by the patch.
if grep -q 'Predicate.isUndefined(choice) && Predicate.isUndefined(event.usage)' \
       packages/ai/openrouter/src/OpenRouterLanguageModel.ts; then
  echo "Patch already applied."
  exit 0
fi

git apply --whitespace=nowarn /solution/pr_6117.diff

echo "Patch applied."
