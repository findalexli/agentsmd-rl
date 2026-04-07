FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout 2f7a8ee722e5d451dd2c242c722ea818cc325485 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install zod so tests can import yaml-config-schema.ts via node --experimental-strip-types
RUN npm install --no-save zod

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
