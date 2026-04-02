#!/usr/bin/env bash
set -euo pipefail
cd /workspace/vllm

if grep -q "_resolve_fi_ar_backend" vllm/distributed/device_communicators/flashinfer_all_reduce.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

# 1. Change default in envs.py: "trtllm" → "auto"
python3 << 'PYEOF'
import re

path = "vllm/envs.py"
src = open(path).read()

# Fix class-level annotation default
src = re.sub(
    r'(VLLM_FLASHINFER_ALLREDUCE_BACKEND:\s*Literal\[.*?\]\s*=\s*)"trtllm"',
    r'\1"auto"',
    src,
)

# Fix env_with_choices default
src = re.sub(
    r'(env_with_choices\(\s*"VLLM_FLASHINFER_ALLREDUCE_BACKEND",\s*)"trtllm"',
    r'\1"auto"',
    src,
)

# Remove the outdated TODO comment block about defaulting to trtllm
src = re.sub(
    r'    # "auto" will default to "mnnvl".*?# Should switch back to "auto" if the issue is resolved\.\n',
    '',
    src,
    flags=re.DOTALL,
)

open(path, "w").write(src)
print("envs.py updated")
PYEOF

# 2. Patch flashinfer_all_reduce.py
python3 << 'PYEOF'
path = "vllm/distributed/device_communicators/flashinfer_all_reduce.py"
src = open(path).read()

# Add import for get_node_count
src = src.replace(
    "from vllm.config.compilation import PassConfig\n",
    "from vllm.config.compilation import PassConfig\nfrom vllm.distributed.parallel_state import get_node_count\n",
)

# Add _resolve_fi_ar_backend function before get_fi_ar_workspace
resolve_func = '''

def _resolve_fi_ar_backend() -> str:
    backend = envs.VLLM_FLASHINFER_ALLREDUCE_BACKEND
    if backend != "auto":
        logger.info_once(f"Using flashinfer allreduce backend: {backend}")
        return backend

    if get_node_count() > 1:  # noqa: SIM108
        # Use mnnvl backend for multi-node setup since
        # trtllm backend does not support multi-node allreduce
        backend = "mnnvl"
    else:
        # Currently defaulting to trtllm backend for single-node
        # setup since mnnvl has issues with cudagraph:
        # https://github.com/vllm-project/vllm/issues/35772
        # Should switch back to auto when the issue is resolved.
        backend = "trtllm"

    logger.info_once(f"Auto-selected flashinfer allreduce backend: {backend}")
    return backend


'''
src = src.replace(
    "\ndef get_fi_ar_workspace(",
    resolve_func + "def get_fi_ar_workspace(",
)

# Replace backend assignment + add ValueError check in get_fi_ar_workspace
# Use surrounding context to only match inside get_fi_ar_workspace (not _resolve_fi_ar_backend)
src = src.replace(
    "    backend = envs.VLLM_FLASHINFER_ALLREDUCE_BACKEND\n\n    # Reuse the quant workspace",
    '''    backend = _resolve_fi_ar_backend()

    if get_node_count() > 1 and backend == "trtllm":
        raise ValueError(
            "Flashinfer allreduce is not supported for multi-node allreduce with "
            "'trtllm' backend. Please use 'mnnvl' backend instead."
        )

    # Reuse the quant workspace''',
)

# Add logging after workspace creation in get_fi_ar_workspace
src = src.replace(
    '''    _fi_ar_workspace = _create_workspace(
        backend, world_size, rank, max_token_num, hidden_dim, dtype, group
    )
    return _fi_ar_workspace''',
    '''    _fi_ar_workspace = _create_workspace(
        backend, world_size, rank, max_token_num, hidden_dim, dtype, group
    )
    if _fi_ar_workspace is not None:
        logger.info_once(
            "Initialized FlashInfer Allreduce norm fusion workspace "
            f"with backend={backend}"
        )
    else:
        logger.warning_once(
            "Failed to initialize FlashInfer Allreduce norm fusion workspace "
            f"with backend={backend}"
        )

    return _fi_ar_workspace''',
)

# Add multi-node check to get_fi_ar_quant_workspace
src = src.replace(
    '''    Always uses trtllm backend as it is the only one supporting quantization
    fusion (FP8/FP4).
    """''',
    '''    Always uses trtllm backend as it is the only one supporting quantization
    fusion (FP8/FP4). Returns None for multi-node setups since not supported
    by trtllm backend.
    """''',
)

src = src.replace(
    '''    global _fi_ar_quant_workspace
    if _fi_ar_quant_workspace is not None:
        return _fi_ar_quant_workspace

    # Reuse the non-quant workspace''',
    '''    global _fi_ar_quant_workspace
    if _fi_ar_quant_workspace is not None:
        return _fi_ar_quant_workspace

    if get_node_count() > 1:
        logger.warning_once(
            "Flashinfer allreduce quantization fusion is not supported for "
            "multi-node allreduce. Disabling quant fusion."
        )
        return None

    # Reuse the non-quant workspace''',
)

# Add logging after quant workspace creation
src = src.replace(
    '''    _fi_ar_quant_workspace = _create_workspace(
        "trtllm", world_size, rank, max_token_num, hidden_dim, dtype, group
    )
    return _fi_ar_quant_workspace''',
    '''    _fi_ar_quant_workspace = _create_workspace(
        "trtllm", world_size, rank, max_token_num, hidden_dim, dtype, group
    )
    if _fi_ar_quant_workspace is not None:
        logger.info_once(
            "Initialized FlashInfer Allreduce norm quantization "
            "fusion workspace with backend=trtllm"
        )
    else:
        logger.warning_once(
            "Failed to initialize FlashInfer Allreduce norm quantization "
            "fusion workspace with backend=trtllm"
        )

    return _fi_ar_quant_workspace''',
)

open(path, "w").write(src)
print("flashinfer_all_reduce.py updated")
PYEOF
