FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (before the fix)
RUN git clone https://github.com/huggingface/transformers.git /workspace/transformers \
    && cd /workspace/transformers \
    && git checkout 18f88de7f575410f3ad8a64418abf2572fecb259 \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

# Install transformers base (no torch/GPU/testing extras — config classes only)
RUN cd /workspace/transformers \
    && pip install --no-cache-dir -e . \
    && pip install --no-cache-dir ruff

ENV PYTHONPATH=/workspace/transformers/src
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers