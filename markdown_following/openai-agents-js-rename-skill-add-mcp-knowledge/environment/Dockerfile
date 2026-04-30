FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        grep && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        PyYAML==6.0.2

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout 41c1b89f650a9d18aeb76677f965dcfb06087c90 && \
    git config user.email "task@example.com" && \
    git config user.name "Task Runner"

WORKDIR /workspace/openai-agents-js
