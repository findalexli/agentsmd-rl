#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if grep -q '_forward_static_no_residual' vllm/model_executor/layers/layernorm.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- Fix 1: vllm/ir/ops/layernorm.py ---
# Change dtype casting order: cast x to orig_dtype BEFORE weight multiply
python3 -c "
import re
p = 'vllm/ir/ops/layernorm.py'
s = open(p).read()
old = '''    x = x * torch.rsqrt(variance + epsilon)
    if weight is not None:
        x = x.to(weight.dtype) * weight
    return x.to(orig_dtype)'''
new = '''    x = x * torch.rsqrt(variance + epsilon)
    x = x.to(orig_dtype)
    if weight is not None:
        x = x * weight
    return x'''
assert old in s, f'Pattern not found in {p}'
open(p, 'w').write(s.replace(old, new))
print(f'Patched {p}')
"

# --- Fix 2: vllm/kernels/vllm_c.py ---
# Remove weight.dtype == x.dtype check from dispatch predicate
python3 -c "
p = 'vllm/kernels/vllm_c.py'
s = open(p).read()
old = '''rms_no_var_size = (
    lambda x, weight, epsilon, variance_size=None: variance_size is None
    and (weight is None or weight.dtype == x.dtype)
)
\"\"\"vLLM kernel does not support variance_size parameter or mismatched weight dtype.\"\"\"'''
new = '''rms_no_var_size = lambda x, weight, epsilon, variance_size=None: variance_size is None
\"\"\"vLLM kernel does not support variance_size parameter.\"\"\"'''
assert old in s, f'Pattern not found in {p}'
open(p, 'w').write(s.replace(old, new))
print(f'Patched {p}')
"

# --- Fix 3: vllm/kernels/aiter_ops.py ---
# Remove weight.dtype == x.dtype check from dispatch predicate
python3 -c "
p = 'vllm/kernels/aiter_ops.py'
s = open(p).read()
old = '''rms_no_var_16bit_only = (
    lambda x, weight, epsilon, variance_size=None: variance_size is None
    and x.dtype in (torch.float16, torch.bfloat16)
    and (weight is None or weight.dtype == x.dtype)
)
\"\"\"AITER rms_norm only supports float16 and bfloat16 acts, no var_size override,
and requires weight dtype to match x dtype.\"\"\"'''
new = '''rms_no_var_16bit_only = (
    lambda x, weight, epsilon, variance_size=None: variance_size is None
    and x.dtype
    in (
        torch.float16,
        torch.bfloat16,
    )
)
\"\"\"AITER rms_norm only supports float16 and bfloat16 acts and no var_size override.\"\"\"'''
assert old in s, f'Pattern not found in {p}'
open(p, 'w').write(s.replace(old, new))
print(f'Patched {p}')
"

# --- Fix 4: vllm/kernels/xpu_ops.py ---
# Remove weight.dtype == x.dtype check from dispatch predicate
python3 -c "
p = 'vllm/kernels/xpu_ops.py'
s = open(p).read()
old = '''rms_no_var = lambda x, weight, epsilon, variance_size=None: variance_size is None and (
    weight is None or weight.dtype == x.dtype
)'''
new = 'rms_no_var = lambda x, weight, epsilon, variance_size=None: variance_size is None'
assert old in s, f'Pattern not found in {p}'
open(p, 'w').write(s.replace(old, new))
print(f'Patched {p}')
"

# --- Fix 5: vllm/model_executor/layers/layernorm.py ---
# Add static methods and update GemmaRMSNorm forward_native/forward_cuda
python3 -c "
p = 'vllm/model_executor/layers/layernorm.py'
s = open(p).read()

# 5a: Add static methods after __init__
init_end = '''        self.weight = nn.Parameter(torch.zeros(hidden_size))
        self.variance_epsilon = eps

    def forward_native('''

static_methods = '''        self.weight = nn.Parameter(torch.zeros(hidden_size))
        self.variance_epsilon = eps

    @staticmethod
    def _forward_static_no_residual(
        weight: torch.Tensor,
        variance_epsilon: float,
        x: torch.Tensor,
    ) -> torch.Tensor:
        \"\"\"PyTorch-native implementation equivalent to forward() without residual.\"\"\"
        orig_dtype = x.dtype
        x = x.float()
        variance = x.pow(2).mean(dim=-1, keepdim=True)
        x = x * torch.rsqrt(variance + variance_epsilon)
        x = x * (1.0 + weight.float())
        x = x.to(orig_dtype)
        return x

    @staticmethod
    def _forward_static_with_residual(
        weight: torch.Tensor,
        variance_epsilon: float,
        x: torch.Tensor,
        residual: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        \"\"\"PyTorch-native implementation equivalent to forward() with residual.\"\"\"
        orig_dtype = x.dtype
        x = (
            x.float() + residual.float()
            if orig_dtype == torch.float16
            else x + residual
        )
        residual = x

        x = x.float()
        variance = x.pow(2).mean(dim=-1, keepdim=True)
        x = x * torch.rsqrt(variance + variance_epsilon)
        # Llama does x.to(float16) * w whilst Gemma is (x * w).to(float16)
        # See https://github.com/huggingface/transformers/pull/29402
        x = x * (1.0 + weight.float())
        x = x.to(orig_dtype)
        return x, residual

    def forward_native('''
assert init_end in s, 'Could not find init_end pattern'
s = s.replace(init_end, static_methods)

# 5b: Replace forward_native body
old_native = '''        if residual is None:
            return ir.ops.rms_norm(
                x, self.weight.data.float() + 1.0, self.variance_epsilon
            )
        else:
            orig_dtype = x.dtype
            x = (
                x.float() + residual.float()
                if orig_dtype == torch.float16
                else x + residual
            )
            residual = x
            return ir.ops.rms_norm(
                x, self.weight.data.float() + 1.0, self.variance_epsilon
            ).to(orig_dtype), residual'''
new_native = '''        if residual is None:
            return self._forward_static_no_residual(
                self.weight.data, self.variance_epsilon, x
            )
        else:
            return self._forward_static_with_residual(
                self.weight.data, self.variance_epsilon, x, residual
            )'''
assert old_native in s, 'Could not find old forward_native body'
s = s.replace(old_native, new_native)

# 5c: Add torch.compile to forward_cuda
old_cuda = '''    def forward_cuda(
        self,
        x: torch.Tensor,
        residual: torch.Tensor | None = None,
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
        return self.forward_native(x, residual)'''
new_cuda = '''    def forward_cuda(
        self,
        x: torch.Tensor,
        residual: torch.Tensor | None = None,
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
        if torch.compiler.is_compiling():
            return self.forward_native(x, residual)

        if not getattr(self, \"_is_compiled\", False):
            self._forward_static_no_residual = torch.compile(  # type: ignore
                self._forward_static_no_residual
            )
            self._forward_static_with_residual = torch.compile(  # type: ignore
                self._forward_static_with_residual
            )
            self._is_compiled = True
        return self.forward_native(x, residual)'''
assert old_cuda in s, 'Could not find old forward_cuda body'
s = s.replace(old_cuda, new_cuda)

open(p, 'w').write(s)
print(f'Patched {p}')
"

echo "Patch applied successfully."
