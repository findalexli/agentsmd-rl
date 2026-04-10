FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (pre-fix)
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 0b943a4fd0d7701203f1b79b70b5afed19ee8413 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Install gradio and its dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory
RUN mkdir -p /logs/verifier
