FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout 80a52899ea6a74e0738c15228181ef7b9775dfe9 && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# No heavy deps needed — tests use AST parsing only
# (importing the modules requires torch/distributed which is GPU-only)

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl