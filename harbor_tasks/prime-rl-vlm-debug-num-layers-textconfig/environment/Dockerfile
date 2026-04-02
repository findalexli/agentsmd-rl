FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git clone https://github.com/PrimeIntellect-ai/prime-rl.git /workspace && \
    cd /workspace && \
    git checkout c2dfc338c30d04286284b67cf87e73d534e43f3e && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# No heavy deps needed — tests only exercise pure Python config logic
ENV PYTHONPATH="/workspace/src:${PYTHONPATH}"
RUN mkdir -p /logs/verifier

WORKDIR /workspace