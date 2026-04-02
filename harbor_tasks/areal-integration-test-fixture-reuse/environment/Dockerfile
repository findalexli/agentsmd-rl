FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
ARG BASE_COMMIT=dfeab6396380f27be96ccb7cb642b57a5a25ef58
RUN git clone https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout ${BASE_COMMIT} && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install minimal deps for testing (no torch/GPU — tests use AST analysis)
# Justification: the test modules transitively import torch, transformers,
# sglang, and other GPU-dependent packages. We verify test structure via AST.
RUN pip install --no-cache-dir pyyaml

ENV PYTHONPATH=/workspace/AReaL
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL