FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin 2648c19e21f949812afbf6e42a42c57decbf4b94 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

# Install CPU-only torch (needed by prime_rl.utils.utils transitive import)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install lightweight deps needed for config module imports
# NOTE: project uses a custom pydantic-config fork (samsja) that exports BaseConfig;
#       the PyPI package (jordantshaw) only exports SettingsModel/SettingsConfig.
RUN pip install --no-cache-dir pydantic 'git+https://github.com/samsja/pydantic_config.git' wandb transformers loguru numpy

# Install project editable without pulling heavy GPU deps (vllm, flash-attn, etc.)
RUN pip install --no-cache-dir --no-deps -e .

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
