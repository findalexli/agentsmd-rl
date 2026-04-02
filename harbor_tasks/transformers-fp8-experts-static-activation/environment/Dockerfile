FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/huggingface/transformers.git /repo && \
    cd /repo && \
    git checkout f6195948b47f06444a7bdf5f169197ed64b64de2

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install torch CPU-only + triton (needed to import finegrained_fp8 module)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir triton

# Install transformers with base deps only
RUN pip install --no-cache-dir -e .

# Install ruff for config-derived lint check + pytest for test runner
RUN pip install --no-cache-dir ruff pytest pytest-json-ctrf

RUN git config user.name "solver" && \
    git config user.email "solver@bench"

ENV PYTHONPATH=/repo/src