FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

# Clone vllm at the commit BEFORE the fix
RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin af89140efc06c462ae531999b9f2db6ba0c7a528 && \
    git checkout FETCH_HEAD

ENV PYTHONPATH="/workspace/vllm"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/vllm