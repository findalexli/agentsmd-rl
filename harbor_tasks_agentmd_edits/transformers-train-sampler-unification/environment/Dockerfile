FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for speed — transformers is huge)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 8efd81513f51cd343d086e0e8f69190caa49dbcf && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

# Install CPU-only torch + transformers editable for TrainingArguments import
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir accelerate && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest pytest-json-ctrf ruff

RUN mkdir -p /logs/verifier
