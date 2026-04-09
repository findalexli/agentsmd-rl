FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout d815881739689f45f5387ea52cc92e2cddf8adcf && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
