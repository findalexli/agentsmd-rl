FROM oven/bun:1-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates python3 && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=3a0e00dd7f9192730f6d0eeee37ae0a5fb023927
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install monorepo deps so bun can resolve TypeScript imports
RUN bun install

RUN mkdir -p /logs/verifier
