FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (BEFORE the fix)
RUN git clone https://github.com/THUDM/slime.git /workspace/slime \
    && cd /workspace/slime \
    && git checkout 243d0883b90e407ee56a6a51d2d8d80fe5cae47e

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

# Configure git for potential patches
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH="/workspace/slime:${PYTHONPATH:-}"