FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (use --filter=blob:none for large monorepo)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout c300a63cc9e0b9eeea6632f0b2150114de8c5d23 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Install Python dependencies for test runner
RUN pip3 install --break-system-packages --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
