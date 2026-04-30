FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 22 (LTS) - required for Playwright TypeScript project
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout f6e14f9d73b46ab319b334c013094d867d4ef149 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install npm dependencies (required for running CI commands)
RUN npm ci

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
