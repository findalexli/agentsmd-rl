FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (pre-fix)
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout 1af6f78ae5a1bd3d70f32d47fe4901bda5c97fdd && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vllm

# Install only what test_outputs.py needs — NOT full vllm (torch/CUDA too heavy)
# _parse_gemma4_args is pure Python but its module import chain pulls in vllm deps,
# so tests extract and execute the function in isolation via subprocess.
RUN pip install --no-cache-dir regex

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
