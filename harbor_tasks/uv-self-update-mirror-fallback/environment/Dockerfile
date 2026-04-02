FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git clone --filter=blob:none --no-checkout https://github.com/astral-sh/uv.git /workspace/uv \
    && cd /workspace/uv \
    && git checkout 7228ad62b9de7f9b5d887ef4b2be9bb033a04191 \
    && git config user.email "agent@test" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/uv