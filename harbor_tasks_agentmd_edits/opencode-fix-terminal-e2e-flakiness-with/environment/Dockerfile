FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout c9c0318e0e5c2fcd80fc1c32a1ccfe360f182f90 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install minimal deps needed by test_outputs.py
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    pip3 install pytest pytest-json-ctrf 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
