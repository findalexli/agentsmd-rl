#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pytorch

TARGET="torch/_dynamo/decorators.py"

# Idempotency: check if already applied
if grep -q '# if einops.__version__ >= "0.8.2":' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Comment out the version check block that causes lru_cache warning spam.
# The fix comments out the early-return branch so allow_in_graph is always applied.
python3 -c "
import re

with open('$TARGET', 'r') as f:
    content = f.read()

# The block to comment out (inside _allow_in_graph_einops):
#     if einops.__version__ >= \"0.8.2\":
#         if hasattr(einops, \"einops\") and hasattr(einops.einops, \"get_backend\"):
#             ...
#         # einops 0.8.2+ don't need explicit allow_in_graph calls
#         return
old = '''    if einops.__version__ >= \"0.8.2\":
        if hasattr(einops, \"einops\") and hasattr(einops.einops, \"get_backend\"):
            # trigger backend registration up front to avoid a later guard failure
            # that would otherwise cause a recompilation
            einops.rearrange(torch.randn(1), \"i -> i\")

        # einops 0.8.2+ don't need explicit allow_in_graph calls
        return'''

new = '''    # There is a lru_cache logspam issue with einops when allow_in_graph is not
    # used. Disabling this for now until the lru_cache issue is resolved.
    # if einops.__version__ >= \"0.8.2\":
    #     if hasattr(einops, \"einops\") and hasattr(einops.einops, \"get_backend\"):
    #         # trigger backend registration up front to avoid a later guard failure
    #         # that would otherwise cause a recompilation
    #         einops.rearrange(torch.randn(1), \"i -> i\")
    #     # einops 0.8.2+ don't need explicit allow_in_graph calls
    #     return'''

assert old in content, 'Could not find the version check block to patch'
content = content.replace(old, new)

with open('$TARGET', 'w') as f:
    f.write(content)
"

echo "Patch applied successfully."
