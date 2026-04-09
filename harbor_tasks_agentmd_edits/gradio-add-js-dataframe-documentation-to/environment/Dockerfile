FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout f67faa464add0ef6a4a58d60eb2ae850125ebb87 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Install minimal Python deps for test runner
RUN pip install --no-cache-dir pytest --break-system-packages

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
