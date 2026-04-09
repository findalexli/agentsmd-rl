FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang at base commit (before the fix)
RUN git clone --depth=200 --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git fetch --depth=200 origin 5e2b0f860c020bfa49ad280203b98941500757f1 && \
    git checkout 5e2b0f860c020bfa49ad280203b98941500757f1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Add repo to PYTHONPATH so imports work
ENV PYTHONPATH="/workspace/sglang/python:$PYTHONPATH"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
