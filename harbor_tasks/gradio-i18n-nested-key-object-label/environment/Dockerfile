FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 9487b60670f6532eaccb3251d15f5505fa23d4e3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
