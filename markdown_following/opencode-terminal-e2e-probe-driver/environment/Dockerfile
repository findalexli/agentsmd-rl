FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (opencode is a large monorepo)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin c9c0318e0e5c2fcd80fc1c32a1ccfe360f182f90 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

RUN mkdir -p /logs/verifier
