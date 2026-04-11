FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout 57e76686346beeaaec4010ebefc56b9949686457 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime"

# Install CPU-only torch + mbridge + safetensors + transformers + megatron-core for test_outputs.py
RUN pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir mbridge safetensors transformers numpy megatron-core einops

# Create a comprehensive fake transformer-engine package to satisfy megatron-core
# This is needed because transformer-engine requires CUDA and is not easily installable in CPU-only environments
RUN python3 << 'MOCKSCRIPT'
from pathlib import Path
from unittest.mock import MagicMock

base = Path('/usr/local/lib/python3.12/site-packages/transformer_engine')
base.mkdir(parents=True, exist_ok=True)

# Metaclass that returns MagicMock for any attribute access
class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

# Main __init__.py
main_init = '''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

# Mock all the classes and functions that megatron imports
Linear = RecursiveMock
LayerNorm = RecursiveMock
RMSNorm = RecursiveMock
LayerNormLinear = RecursiveMock
DotProductAttention = RecursiveMock
GroupedLinear = RecursiveMock
QuantizedTensor = RecursiveMock
Fp8Padding = RecursiveMock
Fp8Unpadding = RecursiveMock
fp8_autocast = RecursiveMock
FP8GlobalStateManager = RecursiveMock
quantized_model_init = RecursiveMock
fp8_model_init = RecursiveMock
cpu_offload_v1 = RecursiveMock

class ops(metaclass=MockMeta):
    SwiGLU = RecursiveMock
    GEGLU = RecursiveMock
    ReGLU = RecursiveMock
    GELU = RecursiveMock
    ReLU = RecursiveMock
    Sequential = RecursiveMock
    LayerNorm = RecursiveMock
    RMSNorm = RecursiveMock
    BasicLinear = RecursiveMock
    Bias = RecursiveMock
    ReduceScatter = RecursiveMock
    AllReduce = RecursiveMock
    FusibleOperation = RecursiveMock
    SiLU = RecursiveMock

class common(metaclass=MockMeta):
    class recipe(metaclass=MockMeta):
        DelayedScaling = RecursiveMock
        Float = RecursiveMock
        class Format(metaclass=MockMeta):
            E = RecursiveMock
            HYBRID = RecursiveMock
        MXFP = RecursiveMock
        NVFP = RecursiveMock

__version__ = "2.0.0"

# Import submodules to register them
from . import pytorch
'''
(base / '__init__.py').write_text(main_init)

# pytorch __init__.py
pytorch_dir = base / 'pytorch'
pytorch_dir.mkdir(exist_ok=True)
pytorch_init = '''from unittest.mock import MagicMock
import transformer_engine

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

# Re-export from parent
Linear = transformer_engine.Linear
LayerNorm = transformer_engine.LayerNorm
RMSNorm = transformer_engine.RMSNorm
LayerNormLinear = transformer_engine.LayerNormLinear
DotProductAttention = transformer_engine.DotProductAttention
GroupedLinear = transformer_engine.GroupedLinear
QuantizedTensor = transformer_engine.QuantizedTensor
Fp8Padding = transformer_engine.Fp8Padding
Fp8Unpadding = transformer_engine.Fp8Unpadding
fp8_autocast = transformer_engine.fp8_autocast
FP8GlobalStateManager = transformer_engine.FP8GlobalStateManager
quantized_model_init = transformer_engine.quantized_model_init
fp8_model_init = transformer_engine.fp8_model_init
cpu_offload_v1 = transformer_engine.cpu_offload_v1
ops = transformer_engine.ops

# Import submodules to register them
from . import distributed, attention, cpu_offload, permutation, cross_entropy
from . import cpp_extensions, module, router, tensor, fp8, optimizers, float8_tensor
'''
(pytorch_dir / '__init__.py').write_text(pytorch_init)

# Create tensor package
tensor_dir = pytorch_dir / 'tensor'
tensor_dir.mkdir(exist_ok=True)
tensor_init = '''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

QuantizedTensor = RecursiveMock
Float8Tensor = RecursiveMock
MXFP8Tensor = RecursiveMock
Float8BlockwiseQTensor = RecursiveMock
NVFP4Tensor = RecursiveMock

from . import utils, mxfp8_tensor, float8_blockwise_tensor, nvfp4_tensor
'''
(tensor_dir / '__init__.py').write_text(tensor_init)

# tensor/utils.py
tensor_utils_dir = tensor_dir / 'utils'
tensor_utils_dir.mkdir(exist_ok=True)
(tensor_utils_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

cast_master_weights_to_fp8 = RecursiveMock
post_all_gather_processing = RecursiveMock
''')

# tensor submodules
(mxfp8_dir := tensor_dir / 'mxfp8_tensor').mkdir(exist_ok=True)
(mxfp8_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

MXFP8Tensor = RecursiveMock
''')

(float8_block_dir := tensor_dir / 'float8_blockwise_tensor').mkdir(exist_ok=True)
(float8_block_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

Float8BlockwiseQTensor = RecursiveMock
''')

(nvfp4_dir := tensor_dir / 'nvfp4_tensor').mkdir(exist_ok=True)
(nvfp4_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

NVFP4Tensor = RecursiveMock
''')

# float8_tensor submodule under tensor (megatron imports from here too)
(tensor_float8_dir := tensor_dir / 'float8_tensor').mkdir(exist_ok=True)
(tensor_float8_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

Float8Tensor = RecursiveMock
''')

# distributed package
dist_dir = pytorch_dir / 'distributed'
dist_dir.mkdir(exist_ok=True)
(dist_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

checkpoint = RecursiveMock
activation_recompute_forward = RecursiveMock
CudaRNGStatesTracker = RecursiveMock
''')

# attention package
attn_dir = pytorch_dir / 'attention'
attn_dir.mkdir(exist_ok=True)
(attn_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

apply_rotary_pos_emb = RecursiveMock
_SplitAlongDim = RecursiveMock
''')

# fp8 package
fp8_dir = pytorch_dir / 'fp8'
fp8_dir.mkdir(exist_ok=True)
(fp8_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

FP8GlobalStateManager = RecursiveMock
fp8_autocast = RecursiveMock
''')

# float8_tensor package
(float8_dir := pytorch_dir / 'float8_tensor').mkdir(exist_ok=True)
(float8_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

Float8Tensor = RecursiveMock
''')

# cpu_offload package
cpu_offload_dir = pytorch_dir / 'cpu_offload'
cpu_offload_dir.mkdir(exist_ok=True)
(cpu_offload_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()
''')

# permutation package
perm_dir = pytorch_dir / 'permutation'
perm_dir.mkdir(exist_ok=True)
(perm_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()
''')

# cross_entropy package
cross_entropy_dir = pytorch_dir / 'cross_entropy'
cross_entropy_dir.mkdir(exist_ok=True)
(cross_entropy_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

parallel_cross_entropy = RecursiveMock
''')

# cpp_extensions package
cpp_dir = pytorch_dir / 'cpp_extensions'
cpp_dir.mkdir(exist_ok=True)
(cpp_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

general_gemm = RecursiveMock
''')

# module package
module_dir = pytorch_dir / 'module'
module_dir.mkdir(exist_ok=True)
(module_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()
''')

# module/base package
module_base_dir = module_dir / 'base'
module_base_dir.mkdir(exist_ok=True)
(module_base_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

TransformerEngineBaseModule = RecursiveMock
get_workspace = RecursiveMock
''')

# router package
router_dir = pytorch_dir / 'router'
router_dir.mkdir(exist_ok=True)
(router_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()
''')

# optimizers package
opt_dir = pytorch_dir / 'optimizers'
opt_dir.mkdir(exist_ok=True)
(opt_dir / '__init__.py').write_text('''from unittest.mock import MagicMock

class MockMeta(type):
    def __getattr__(cls, name):
        return MagicMock()

class RecursiveMock(metaclass=MockMeta):
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()

multi_tensor_applier = RecursiveMock
multi_tensor_scale = RecursiveMock
''')

# Create dist-info
distinfo = Path('/usr/local/lib/python3.12/site-packages/transformer_engine-2.0.0.dist-info')
distinfo.mkdir(exist_ok=True)
(distinfo / 'METADATA').write_text('''Metadata-Version: 2.1
Name: transformer-engine
Version: 2.0.0''')

print('Mock transformer_engine package created successfully!')
MOCKSCRIPT

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
