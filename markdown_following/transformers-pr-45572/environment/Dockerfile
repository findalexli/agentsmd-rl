FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/transformers

# Clone at base commit
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    git checkout 628c54c23d73cf2bf04816e9168d41deb33b1a2f

RUN pip install --no-cache-dir \
    torch==2.5.1 \
    pytest==8.3.4 \
    numpy==2.0.2

# Install transformers from source with minimal deps
RUN pip install --no-cache-dir -e ".[torch]" && \
    pip install --no-cache-dir safetensors==0.5.3

RUN mkdir -p /logs/verifier

# Pre-run a quick import check
RUN python -c "from transformers.models.dots1.modeling_dots1 import Dots1MoE; print('import ok')"
