FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at the base commit (BEFORE the fix)
RUN git clone https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout 27c35b1ce136c85c120b0486128316ae022b53a5

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl

# No heavy deps needed — tests mock torch/wandb and call the decorator directly