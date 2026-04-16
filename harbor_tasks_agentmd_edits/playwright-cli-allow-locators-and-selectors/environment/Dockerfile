FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 35f853d5c293c901ea66a9aa3f56f6879a94e66a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install dependencies and build
RUN npm ci && npm run build

# Install pytest for test runner
RUN pip3 install --no-cache-dir pytest --break-system-packages

# Verifier output directory
RUN mkdir -p /logs/verifier
