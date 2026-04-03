FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin 2bf5b70ae86261431b4b92276828b40b9c0903b6 && \
    git checkout FETCH_HEAD

# Install minimal deps (agent fills in specifics)
RUN pip install --no-cache-dir numpy 2>/dev/null || true

ENV PYTHONPATH="/workspace/vllm"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/vllm