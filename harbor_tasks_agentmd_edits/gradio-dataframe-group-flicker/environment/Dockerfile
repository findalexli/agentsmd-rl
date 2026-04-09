FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies for Playwright + Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux \
        # Playwright dependencies (Chromium minimal)
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pytest playwright --break-system-packages

# Install Playwright Chromium browser (minimal for CSS testing)
RUN npx playwright install chromium

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 339811ee0d6f750e18a9ddc8e9c9bb036e328535 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
