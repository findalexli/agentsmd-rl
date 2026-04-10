#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

python3 << 'PYTHON_SCRIPT'
import re

with open("src/prime_rl/trainer/ckpt.py", "r") as f:
    content = f.read()

# Check if already applied
if "gc.collect()" in content:
    print("Patch already applied.")
    exit(0)

# 1. Add 'import gc' after 'import bisect'
content = content.replace("import bisect\n", "import bisect\nimport gc\n")

# 2. Replace the CPU offload loop with the tracking version
old_loop = """        # Re-initialize CPU offload wrappers after loading
        for opt in self.optimizers:
            if isinstance(opt, CPUOffloadOptimizer):
                opt._move_states("cpu")
                opt._initialized = True"""

new_loop = """        # Re-initialize CPU offload wrappers after loading
        has_cpu_offload = False
        for opt in self.optimizers:
            if isinstance(opt, CPUOffloadOptimizer):
                opt._move_states("cpu")
                opt._initialized = True
                has_cpu_offload = True"""

content = content.replace(old_loop, new_loop)

# 3. Add memory cleanup after the progress setattr loop
# Use a more targeted comment - single line instead of explaining process
old_end = """        if self.progress is not None:
            for key, value in state_dict["progress"].items():
                setattr(self.progress, key, value)


class CheckpointManager:"""

new_end = """        if self.progress is not None:
            for key, value in state_dict["progress"].items():
                setattr(self.progress, key, value)

        if has_cpu_offload:
            state_dict.clear()
            gc.collect()
            torch.cuda.empty_cache()


class CheckpointManager:"""

content = content.replace(old_end, new_end)

with open("src/prime_rl/trainer/ckpt.py", "w") as f:
    f.write(content)

print("Patch applied successfully.")
PYTHON_SCRIPT
