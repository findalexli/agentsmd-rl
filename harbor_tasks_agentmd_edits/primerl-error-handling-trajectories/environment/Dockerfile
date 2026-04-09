FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout e6277883011bed744a066cec86b86d5a82236ba3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

ENV PYTHONPATH="/workspace/prime-rl/src"

# Install minimal deps needed by test_outputs.py (msgspec for TrainingSample, verifiers tomli for vf.State)
# We install only what's needed for tests, NOT the full project deps
RUN pip install --no-cache-dir pytest msgspec pytest-json-ctrf verifiers tomli

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
