FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout ce769774350ad70fe94f5ab17485177751793097 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/slime

# Install torch CPU-only + safetensors (needed by test_outputs.py to test
# the weight conversion logic without a GPU)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir safetensors

RUN mkdir -p /logs/verifier
