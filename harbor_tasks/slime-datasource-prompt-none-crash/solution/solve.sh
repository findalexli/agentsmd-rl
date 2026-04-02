#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency check
if grep -q 'args.prompt_data is not None' slime/rollout/data_source.py; then
    echo "Patch already applied"
    exit 0
fi

# --- Patch data_source.py ---
# 1. Constructor: guard dataset loading on prompt_data not being None
sed -i 's/if args.rollout_global_dataset:/if args.rollout_global_dataset and args.prompt_data is not None:/' \
    slime/rollout/data_source.py

# 2. __len__: return 0 when dataset is None
sed -i '/def __len__(self) -> int:/a\        if self.dataset is None:\n            return 0' \
    slime/rollout/data_source.py

# 3. load(): guard shuffle call on dataset not being None
sed -i 's/if self.args.rollout_global_dataset and self.args.rollout_shuffle:/if self.args.rollout_global_dataset and self.args.rollout_shuffle and self.dataset is not None:/' \
    slime/rollout/data_source.py

# --- Patch ray/rollout.py ---
# Add disable_health_check = True after disable_circuit_breaker line
sed -i '/router_args.disable_circuit_breaker = True/a\
\n        # We will not use the health check from router.\n        router_args.disable_health_check = True' \
    slime/ray/rollout.py

echo "Patch applied successfully"
