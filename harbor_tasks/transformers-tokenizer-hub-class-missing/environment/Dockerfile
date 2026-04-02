FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=huggingface/transformers
ARG COMMIT=c55f65056becad6df5f7eef7ce74ac0811fdfac6

RUN git clone --filter=blob:none https://github.com/${REPO}.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout ${COMMIT} && \
    git config user.email "bench@test.com" && \
    git config user.name "Bench"

# Install CPU-only torch (needed for tokenization_auto imports) + ruff for style checks
RUN cd /workspace/transformers && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pyyaml ruff

ENV PYTHONPATH=/workspace/transformers/src
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers