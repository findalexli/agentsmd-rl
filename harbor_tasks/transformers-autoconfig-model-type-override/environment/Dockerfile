FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global advice.detachedHead false

# Clone transformers at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers \
    && cd /workspace/transformers \
    && git checkout ce4a791c5277840c4c1d74eed03431b674869da5

# Install transformers in editable mode (minimal — no torch, no GPU)
RUN cd /workspace/transformers && pip install --no-cache-dir -e .
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Configure git for agent commits
RUN cd /workspace/transformers && git config user.name "agent" && git config user.email "agent@test"

ENV PYTHONPATH="/workspace/transformers/src"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers