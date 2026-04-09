FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout 6208006db64ac29aded7be33963e86503ba9e28e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/AReaL

# Install torch CPU-only (needed by Platform base class and torch.device)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
