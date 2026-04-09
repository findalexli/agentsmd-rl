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
    git checkout 6f6fa002a55a26ba1cc33aa9ac6b7301f59b82e0 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

ENV PYTHONPATH="/workspace/prime-rl"

# Install minimal deps needed by test_outputs.py
# Need tomli_w for config writing test, jinja2 is in repo deps
RUN pip install --no-cache-dir pytest tomli_w jinja2

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
