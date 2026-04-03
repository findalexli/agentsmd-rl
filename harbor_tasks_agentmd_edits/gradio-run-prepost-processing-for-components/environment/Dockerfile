FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 835e4bd1adcaf5716283fa379e909f916a032b8a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Tests import gradio.profiling directly (stdlib-only), read source files,
# and check README content. No heavy deps needed.
RUN pip install --no-cache-dir anyio

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
