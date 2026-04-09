FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (sglang is large, use --depth=500 for recent history)
RUN git clone --depth=500 https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout c3c13dd5e3b42850d5a96adca4092deb72bf1e4a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install pytest + pytest-json-ctrf for test runner (Python's ast module is built-in)
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Pre-install minimal sglang deps needed to parse test files (mock torch for import checks)
RUN pip install --no-cache-dir torch numpy requests || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
