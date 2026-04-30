#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotent: skip if already applied
if grep -q host_total_GB slime/utils/memory_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
# Read the file
with open("slime/utils/memory_utils.py", "r") as f:
    content = f.read()

# Add psutil import after "import logging"
content = content.replace(
    "import logging\n\nimport torch",
    "import logging\n\nimport psutil\nimport torch"
)

# Add vm = psutil.virtual_memory() after mem_get_info line  
content = content.replace(
    "free, total = torch.cuda.mem_get_info(device)\n    return {",
    "free, total = torch.cuda.mem_get_info(device)\n    vm = psutil.virtual_memory()\n    return {"
)

# Add host memory keys to the return dict
old_str = '"reserved_GB": _byte_to_gb(torch.cuda.memory_reserved(device)),'
new_str = '"reserved_GB": _byte_to_gb(torch.cuda.memory_reserved(device)),\n        "host_total_GB": _byte_to_gb(vm.total),\n        "host_available_GB": _byte_to_gb(vm.available),\n        "host_used_GB": _byte_to_gb(vm.used),\n        "host_free_GB": _byte_to_gb(vm.free),'
content = content.replace(old_str, new_str)

# Write the file
with open("slime/utils/memory_utils.py", "w") as f:
    f.write(content)

print("Patch applied successfully.")
PYEOF
