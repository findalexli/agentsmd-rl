FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=03d71153a72581d83df72d69c30586a41ba71665

RUN git clone https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout ${BASE_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL

# Install minimal deps needed for testing (no torch/GPU packages)
# Tests extract config dataclasses from source and call them directly
RUN pip install --no-cache-dir pyyaml

# Configure git for any agent that wants to commit
RUN git config --global user.email "agent@test.local" && \
    git config --global user.name "Test Agent"

ENV PYTHONPATH="/workspace/AReaL:${PYTHONPATH:-}"