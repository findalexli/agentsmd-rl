FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO_URL=https://github.com/PrimeIntellect-ai/prime-rl.git
ARG BASE_COMMIT=d7afbaa6f39930f801912e1ebb78e0c04ba18ff8

RUN git clone "$REPO_URL" /repo && \
    cd /repo && \
    git checkout "$BASE_COMMIT" && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install minimal deps for CPU-based testing (no GPU, no flash-attn, no vllm)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    "transformers>=4.48" \
    pydantic \
    pydantic-settings \
    tyro \
    annotated-types \
    pyyaml \
    liger-kernel

# Install pydantic-config from the same source the repo uses
RUN pip install --no-cache-dir "pydantic-config @ git+https://github.com/samsja/pydantic_config.git@main"

RUN pip install --no-cache-dir pytest pytest-json-ctrf

ENV PYTHONPATH=/repo/src
RUN mkdir -p /logs/verifier

WORKDIR /repo