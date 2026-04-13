#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q '_detect_gfx95_quant_format' python/sglang/srt/models/deepseek_v2.py 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

# Use Python to apply the changes reliably
python3 << 'EOF'
import re

TARGET = 'python/sglang/srt/models/deepseek_v2.py'
with open(TARGET, 'r') as f:
    content = f.read()

# 1. Add _gfx95_quant_format initialization in __init__ after post_attention_layernorm
init_pattern = r'(self\.post_attention_layernorm = RMSNorm\(\s*\n\s*config\.hidden_size, eps=config\.rms_norm_eps\s*\n\s*\))'
init_replacement = r'''\1

        self._gfx95_quant_format = self._detect_gfx95_quant_format()'''

content = re.sub(init_pattern, init_replacement, content)

# 2. Add _detect_gfx95_quant_format method before _is_layer_sparse
new_method = '''    def _detect_gfx95_quant_format(self) -> str:
        if not _is_gfx95_supported:
            return ""
        weight = getattr(
            getattr(self.self_attn, "fused_qkv_a_proj_with_mqa", None), "weight", None
        )
        if weight is None:
            return ""
        if weight.dtype == torch.uint8:
            return "mxfp4"
        if weight.dtype == getattr(torch, "float8_e4m3fn", None):
            return "fp8"
        return ""

'''

is_layer_pattern = r'(    def _is_layer_sparse\(self, layer_id: int, is_nextn: bool\) -> bool:)'
content = re.sub(is_layer_pattern, new_method + r'\1', content)

# 3. Replace the quant_format computation in forward with self._gfx95_quant_format
old_quant_format = '''        quant_format = (
            "mxfp4"
            if (
                _is_gfx95_supported
                and getattr(self.self_attn, "fused_qkv_a_proj_with_mqa", None)
                is not None
                and getattr(self.self_attn.fused_qkv_a_proj_with_mqa, "weight", None)
                is not None
                and self.self_attn.fused_qkv_a_proj_with_mqa.weight.dtype == torch.uint8
            )
            else (
                "fp8"
                if (
                    _is_gfx95_supported
                    and getattr(self.self_attn, "fused_qkv_a_proj_with_mqa", None)
                    is not None
                    and getattr(
                        self.self_attn.fused_qkv_a_proj_with_mqa, "weight", None
                    )
                    is not None
                    and self.self_attn.fused_qkv_a_proj_with_mqa.weight.dtype
                    == getattr(torch, "float8_e4m3fn", None)
                )
                else ""
            )
        )

        hidden_states, residual = self.layer_communicator.prepare_attn(
            hidden_states,
            residual,
            forward_batch,
            quant_format,
        )'''

new_quant_format = '''        hidden_states, residual = self.layer_communicator.prepare_attn(
            hidden_states,
            residual,
            forward_batch,
            self._gfx95_quant_format,
        )'''

content = content.replace(old_quant_format, new_quant_format)

with open(TARGET, 'w') as f:
    f.write(content)

print('Patch applied successfully.')
EOF

echo 'Patch applied successfully.'
