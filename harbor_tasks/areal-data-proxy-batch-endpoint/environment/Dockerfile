FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
ARG BASE_COMMIT=0405b5c30c815044d858f15d04d2033c9a3d7760
RUN git clone https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout ${BASE_COMMIT} && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install minimal deps for testing (no torch/GPU — tests use source analysis)
# Justification: the data proxy module transitively imports torch, transformers,
# datasets, peft, and many other heavy GPU-oriented packages. Installing the full
# dep chain would exceed CPU-only container constraints. The fix is a FastAPI route
# registration, tested via source/AST analysis.
RUN pip install --no-cache-dir \
    fastapi httpx orjson pydantic pyyaml

ENV PYTHONPATH=/workspace/AReaL
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL