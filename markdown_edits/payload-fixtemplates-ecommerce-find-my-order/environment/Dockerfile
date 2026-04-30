FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies + Python for test runner
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git checkout 7f3c6c8f4628fb066002e2fd5c3cc6b83ddf4ccc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
