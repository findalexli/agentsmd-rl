FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm globally (needed for MCP CI tests)
RUN npm install -g pnpm

# Clone repo at base commit (shallow — monorepo is large)
RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin 2f7a8ee722e5d451dd2c242c722ea818cc325485 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
