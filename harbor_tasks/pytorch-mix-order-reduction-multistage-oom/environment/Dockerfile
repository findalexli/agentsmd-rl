FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone pytorch at base commit (before the fix)
RUN git init /workspace/pytorch && \
    cd /workspace/pytorch && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin 5d919bfe0f2ba7c7aabdb75ef6a20512f163e662 && \
    git checkout FETCH_HEAD

ENV PYTHONPATH="/workspace/pytorch"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/pytorch