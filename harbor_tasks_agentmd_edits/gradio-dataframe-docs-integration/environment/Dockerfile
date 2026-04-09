FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install python3 for test runner + git + pnpm
RUN apt-get update && \
    apt-get install -y --no-install-no-install-recommends \
        git curl ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    npm install -g pnpm

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 5a4ae4926b9dadefd5cf9d0225f5e8ed69eebb51 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Install minimal Python deps needed by test_outputs.py
RUN python3 -m pip install --break-system-packages pytest pathspec

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
