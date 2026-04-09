FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux wget && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout 49573938857d8834b1917b43ece34f8b52a10fbd && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest numpy
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
# Mock wandb for testing (we don't need real wandb, just to avoid import errors)
RUN pip install --no-cache-dir wandb || echo "wandb install skipped"

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
