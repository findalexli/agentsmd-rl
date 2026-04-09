FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout 09293f3e3eb8bd0fc643bac2d2b80014f0529641 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

# CPU-only torch (avoids CUDA dependency)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Deps for importing config + loss modules
RUN pip install --no-cache-dir \
    pydantic beartype jaxtyping transformers \
    "pydantic-config @ git+https://github.com/samsja/pydantic_config.git@main"

ENV PYTHONPATH="/workspace/prime-rl/src"

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
