FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout c0060cf2a695d719152c939cfc3cced8f7da3e52 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react/compiler

# Install and build the compiler (this takes time but ensures tests work)
RUN yarn install --network-timeout 600000 || yarn install --network-timeout 600000

# Build the compiler packages
RUN yarn workspace babel-plugin-react-compiler build || true
RUN yarn workspace snap build || true

# Install minimal deps needed by test_outputs.py
RUN pip3 install --no-cache-dir --break-system-packages pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
