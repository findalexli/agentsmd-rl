FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 0cbbbce8348cbb3254d4f93c48580151fe048daf && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

ENV PYTHONPATH="/workspace/gradio"

# Install only what test_outputs.py needs
RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier
