#!/usr/bin/env bash
set -e

cd /workspace/vllm

# Apply the gold patch from PR #38152: Disable dual stream execution of input
# projection for Qwen3/Qwen3.5

# --- qwen3_next.py changes ---

QWEN3_NEXT="vllm/model_executor/models/qwen3_next.py"

# 1. Fix imports: remove multi_stream_utils and aux_stream, keep direct_register_custom_op
sed -i '/^from vllm\.utils\.multi_stream_utils import maybe_execute_in_parallel$/d' "$QWEN3_NEXT"
sed -i 's/^from vllm\.utils\.torch_utils import (\s*$/from vllm.utils.torch_utils import direct_register_custom_op/' "$QWEN3_NEXT"
sed -i '/^    aux_stream,$/d' "$QWEN3_NEXT"
sed -i '/^    direct_register_custom_op,$/d' "$QWEN3_NEXT"
sed -i '/^)$/{ N; /^)\nfrom vllm\.v1\.attention\.backend/{ s/^)\n/\n/; }; }' "$QWEN3_NEXT"

# 2. Remove aux_stream and events from __init__
python3 << 'PYEOF'
import re

with open("vllm/model_executor/models/qwen3_next.py") as f:
    content = f.read()

# Remove self.aux_stream = aux_stream() line
content = re.sub(r'\n        self\.aux_stream = aux_stream\(\)\n', '\n', content)

# Remove self.events = (...) block
content = re.sub(
    r'\n        self\.events = \(\n'
    r'            \[torch\.cuda\.Event\(\), torch\.cuda\.Event\(\)\]\n'
    r'            if current_platform\.is_cuda_alike\(\)\n'
    r'            else \[None, None\]\n'
    r'        \)\n',
    '\n',
    content
)

with open("vllm/model_executor/models/qwen3_next.py", "w") as f:
    f.write(content)
PYEOF

# 3. Replace forward method's custom op call with direct linear layer calls
python3 << 'PYEOF'
import re

with open("vllm/model_executor/models/qwen3_next.py") as f:
    content = f.read()

old_block = (
    '        projected_states_qkvz, projected_states_ba = torch.ops.vllm.gdn_in_proj(\n'
    '            hidden_states,\n'
    '            sum(self.in_proj_qkvz.output_sizes) // self.tp_size,\n'
    '            sum(self.in_proj_ba.output_sizes) // self.tp_size,\n'
    '            self.prefix,\n'
    '        )'
)
new_block = (
    '        projected_states_qkvz, _ = self.in_proj_qkvz(hidden_states)\n'
    '        projected_states_ba, _ = self.in_proj_ba(hidden_states)'
)

content = content.replace(old_block, new_block)

with open("vllm/model_executor/models/qwen3_next.py", "w") as f:
    f.write(content)
PYEOF

# 4. Remove _forward_in_proj helper method
python3 << 'PYEOF'
import re

with open("vllm/model_executor/models/qwen3_next.py") as f:
    content = f.read()

# Remove _forward_in_proj method
content = re.sub(
    r'\n    def _forward_in_proj\(\n'
    r'        self, hidden_states: torch\.Tensor\n'
    r'    \) -> tuple\[torch\.Tensor, torch\.Tensor\]:\n'
    r'        projected_states_qkvz, projected_states_ba = maybe_execute_in_parallel\(\n'
    r'            lambda: self\.in_proj_qkvz\(hidden_states\)\[0\],\n'
    r'            lambda: self\.in_proj_ba\(hidden_states\)\[0\],\n'
    r'            self\.events\[0\],\n'
    r'            self\.events\[1\],\n'
    r'            self\.aux_stream,\n'
    r'        \)\n'
    r'        return projected_states_qkvz, projected_states_ba\n',
    '\n',
    content
)

with open("vllm/model_executor/models/qwen3_next.py", "w") as f:
    f.write(content)
PYEOF

# 5. Remove gdn_in_proj and gdn_in_proj_fake functions
python3 << 'PYEOF'
import re

with open("vllm/model_executor/models/qwen3_next.py") as f:
    content = f.read()

# Remove gdn_in_proj function
content = re.sub(
    r'\ndef gdn_in_proj\(\n'
    r'    hidden_states: torch\.Tensor,\n'
    r'    qkvz_output_size: int,\n'
    r'    ba_output_size: int,\n'
    r'    layer_name: str,\n'
    r'\) -> tuple\[torch\.Tensor, torch\.Tensor\]:\n'
    r'    """\n'
    r'    Custom op for the input projection\.\n'
    r'    """\n'
    r'    forward_context: ForwardContext = get_forward_context\(\)\n'
    r'    self = forward_context\.no_compile_layers\[layer_name\]\n'
    r'    return self\._forward_in_proj\(hidden_states\)\n',
    '\n',
    content
)

# Remove gdn_in_proj_fake function
content = re.sub(
    r'\ndef gdn_in_proj_fake\(\n'
    r'    hidden_states: torch\.Tensor,\n'
    r'    qkvz_output_size: int,\n'
    r'    ba_output_size: int,\n'
    r'    layer_name: str,\n'
    r'\) -> tuple\[torch\.Tensor, torch\.Tensor\]:\n'
    r'    """Fake implementation for torch\.compile\."""\n'
    r'    return hidden_states\.new_empty\(\n'
    r'        hidden_states\.shape\[0\], qkvz_output_size\n'
    r'    \), hidden_states\.new_empty\(hidden_states\.shape\[0\], ba_output_size\)\n',
    '\n',
    content
)

with open("vllm/model_executor/models/qwen3_next.py", "w") as f:
    f.write(content)
PYEOF

# 6. Remove gdn_in_proj custom op registration
python3 << 'PYEOF'
import re

with open("vllm/model_executor/models/qwen3_next.py") as f:
    content = f.read()

content = re.sub(
    r'\ndirect_register_custom_op\(\n'
    r'    op_name="gdn_in_proj",\n'
    r'    op_func=gdn_in_proj,\n'
    r'    fake_impl=gdn_in_proj_fake,\n'
    r'\)\n',
    '\n',
    content
)

with open("vllm/model_executor/models/qwen3_next.py", "w") as f:
    f.write(content)
PYEOF

# --- qwen3_5.py changes ---

QWEN3_5="vllm/model_executor/models/qwen3_5.py"

# Replace custom op call in forward with direct linear layer calls
python3 << 'PYEOF'
with open("vllm/model_executor/models/qwen3_5.py") as f:
    content = f.read()

old_block = (
    '            mixed_qkvz, ba = torch.ops.vllm.gdn_in_proj(\n'
    '                hidden_states,\n'
    '                sum(self.in_proj_qkvz.output_sizes) // self.tp_size,\n'
    '                sum(self.in_proj_ba.output_sizes) // self.tp_size,\n'
    '                self.prefix,\n'
    '            )'
)
new_block = (
    '            mixed_qkvz, _ = self.in_proj_qkvz(hidden_states)\n'
    '            ba, _ = self.in_proj_ba(hidden_states)'
)

content = content.replace(old_block, new_block)

with open("vllm/model_executor/models/qwen3_5.py", "w") as f:
    f.write(content)
PYEOF

echo "Gold patch applied successfully."
