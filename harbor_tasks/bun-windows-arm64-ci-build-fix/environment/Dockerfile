FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone bun repo at base commit
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout cd4459476a5f0af4e45b8594ac88732ba6d79afb && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Install bun for running TypeScript scripts
RUN npm install -g bun

# Install pytest for test runner
RUN pip3 install --break-system-packages pytest pytest-json-ctrf --quiet

# Verifier output directory
RUN mkdir -p /logs/verifier
