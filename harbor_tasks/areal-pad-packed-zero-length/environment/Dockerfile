FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git clone https://github.com/inclusionAI/AReaL.git /workspace/AReaL \
    && cd /workspace/AReaL \
    && git checkout c961323ec4d989a52c78e5b42fc32f665367949f

WORKDIR /workspace/AReaL

# Install minimal deps needed for testing (CPU-only, no torch ecosystem)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir numpy einops torchdata

# Stub out modules with heavy deps not needed for testing areal.utils.data.
RUN echo '# stubbed' > /workspace/AReaL/areal/__init__.py && \
    echo '# stubbed' > /workspace/AReaL/areal/infra/__init__.py && \
    mkdir -p /workspace /logs/verifier/AReaL/areal/engine/fsdp_utils && \
    echo '' > /workspace/AReaL/areal/engine/__init__.py && \
    echo '' > /workspace/AReaL/areal/engine/fsdp_utils/__init__.py && \
    mkdir -p /workspace /logs/verifier/AReaL/areal/infra/platforms && \
    printf 'class _P:\n    pass\ncurrent_platform = _P()\n' > /workspace/AReaL/areal/infra/platforms/__init__.py && \
    printf 'import logging\ngetLogger = logging.getLogger\n' > /workspace/AReaL/areal/utils/logging.py && \
    printf '# stubbed\n' > /workspace/AReaL/areal/utils/seqpack.py && \
    printf 'from dataclasses import dataclass\n@dataclass\nclass MicroBatchSpec:\n    pass\n@dataclass\nclass NormConfig:\n    pass\n' > /workspace/AReaL/areal/api/cli_args.py

# Set PYTHONPATH so areal is importable
ENV PYTHONPATH=/workspace/AReaL

# Configure git user for potential patch application
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

# Tests are mounted at runtime via -v, not baked into image