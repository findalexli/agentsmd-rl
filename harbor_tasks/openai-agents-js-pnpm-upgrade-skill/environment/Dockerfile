FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-report==1.5.0 \
    pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git && \
    cd openai-agents-js && \
    git checkout 94b4b7c55a6ada0fb0450c95ad6c47e3d6d449f9

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openai-agents-js
