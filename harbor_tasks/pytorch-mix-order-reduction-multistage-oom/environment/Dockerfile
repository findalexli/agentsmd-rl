FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone pytorch at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/pytorch/pytorch.git /workspace/pytorch \
    && cd /workspace/pytorch \
    && git checkout 5d919bfe0f2ba7c7aabdb75ef6a20512f163e662 \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

ENV PYTHONPATH="/workspace/pytorch"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/pytorch