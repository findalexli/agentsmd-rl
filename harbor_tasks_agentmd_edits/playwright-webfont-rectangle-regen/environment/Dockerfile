FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout c1385dc133b5846ffdaf3eafdbb9b46a1be1575d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install deps needed by test_outputs.py and generate_font.py
RUN pip install --no-cache-dir fonttools brotli

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
