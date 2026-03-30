#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

# Idempotent check
if [ -f "areal/trainer/ppo/stats.py" ] && grep -q "infer_token_denominator" areal/trainer/ppo/stats.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create stats.py
cat > areal/trainer/ppo/stats.py << 'STATSEOF'
from __future__ import annotations

from typing import Any

import torch


def infer_token_denominator(
    input_data: dict[str, Any],
    fallback: torch.Tensor,
) -> torch.Tensor:
    """Infer the full token mask for stats logging.

    Context parallelism may slice intermediate tensors such as ``loss_mask`` or
    model outputs, while the original micro-batch metadata still describes the
    full logical sequence. Prefer that metadata for ``n_tokens`` so statistics
    stay consistent with and without context parallelism.
    """
    common_kwargs = {"dtype": torch.bool, "device": fallback.device}

    attention_mask = input_data.get("attention_mask")
    if isinstance(attention_mask, torch.Tensor):
        return torch.ones_like(attention_mask, **common_kwargs)

    cu_seqlens = input_data.get("cu_seqlens")
    if isinstance(cu_seqlens, torch.Tensor) and cu_seqlens.numel() > 0:
        return torch.ones(int(cu_seqlens[-1].item()), **common_kwargs)

    input_ids = input_data.get("input_ids")
    if isinstance(input_ids, torch.Tensor) and input_ids.shape == fallback.shape:
        return torch.ones_like(input_ids, **common_kwargs)

    return torch.ones_like(fallback, **common_kwargs)
STATSEOF

# Patch actor.py
sed -i 's/from areal.utils import logging, stats_tracker/from areal.trainer.ppo.stats import infer_token_denominator\nfrom areal.utils import logging, stats_tracker/' areal/trainer/ppo/actor.py
sed -i 's/n_tokens=torch.ones_like(loss_mask, dtype=torch.bool)/n_tokens=infer_token_denominator(data, loss_mask)/g' areal/trainer/ppo/actor.py
sed -i 's/n_tokens=torch.ones_like(loss_mask, dtype=torch.bool, device=logprobs.device)/n_tokens=infer_token_denominator(input_data, loss_mask)/g' areal/trainer/ppo/actor.py

# Patch critic.py
sed -i 's/from areal.utils import stats_tracker/from areal.trainer.ppo.stats import infer_token_denominator\nfrom areal.utils import stats_tracker/' areal/trainer/ppo/critic.py
sed -i 's/n_tokens=torch.ones(value.shape\[0\], dtype=torch.bool, device=value.device)/n_tokens=infer_token_denominator(input_data, value)/' areal/trainer/ppo/critic.py
