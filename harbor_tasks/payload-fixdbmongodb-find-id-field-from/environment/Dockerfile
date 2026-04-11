FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit
RUN git init /workspace/payload && \
    cd /workspace/payload && \
    git remote add origin https://github.com/payloadcms/payload.git && \
    git fetch --depth=1 origin 5ebda61c74724cf68d2b1b1dc9886dde5f55b0ff && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Install pnpm globally for running tests
RUN npm install -g pnpm

# Verifier output directory
RUN mkdir -p /logs/verifier
