FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone transformers at base commit (before fix)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin a48a63c27d1cdb7845d2c3acc4f11f580917b69b && \
    git checkout FETCH_HEAD

# Install minimal deps for importing config classes and running tests
RUN cd /workspace/transformers && \
    pip install --no-cache-dir -e ".[dev]" 2>/dev/null || \
    pip install --no-cache-dir packaging pyyaml safetensors huggingface_hub regex requests tqdm filelock ruff

ENV PYTHONPATH="/workspace/transformers/src"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers