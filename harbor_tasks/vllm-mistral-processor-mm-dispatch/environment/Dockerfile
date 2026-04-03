FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=43cc5138e5145752413235a2a8aa303886077327

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN git config --global user.email "bench@test" && \
    git config --global user.name "Benchmark"

ENV PYTHONPATH="/repo"
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo