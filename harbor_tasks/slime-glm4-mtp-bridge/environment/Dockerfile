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
    pip install --no-cache-dir mbridge safetensors transformers numpy megatron-core

# Create a fake transformer-engine package to satisfy megatron-core
RUN mkdir -p /usr/local/lib/python3.12/site-packages/transformer_engine/pytorch/tensor && \
    echo "__version__ = '2.0.0'" > /usr/local/lib/python3.12/site-packages/transformer_engine/__init__.py && \
    echo "from unittest.mock import MagicMock\nQuantizedTensor = MagicMock" > /usr/local/lib/python3.12/site-packages/transformer_engine/pytorch/__init__.py && \
    echo "from unittest.mock import MagicMock\nQuantizedTensor = MagicMock" > /usr/local/lib/python3.12/site-packages/transformer_engine/pytorch/tensor/__init__.py && \
    mkdir -p /usr/local/lib/python3.12/site-packages/transformer_engine-2.0.0.dist-info && \
    echo 'Metadata-Version: 2.1' > /usr/local/lib/python3.12/site-packages/transformer_engine-2.0.0.dist-info/METADATA && \
    echo 'Name: transformer-engine' >> /usr/local/lib/python3.12/site-packages/transformer_engine-2.0.0.dist-info/METADATA && \
    echo 'Version: 2.0.0' >> /usr/local/lib/python3.12/site-packages/transformer_engine-2.0.0.dist-info/METADATA

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
