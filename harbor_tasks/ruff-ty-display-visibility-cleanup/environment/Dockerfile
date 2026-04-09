FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff && \
    cd /workspace/ruff && \
    git checkout 162852609ad01f171ba868900d18e57236573785 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/ruff

# Pre-compile ty_python_semantic for fast incremental checks during tests
RUN cargo check -p ty_python_semantic 2>&1 || true

# Install pytest for test runner
RUN python3 -m pip install --no-cache-dir pytest pytest-json-ctrf || \
    pip3 install --no-cache-dir --break-system-packages pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
