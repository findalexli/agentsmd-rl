FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=43cc5138e5145752413235a2a8aa303886077327

RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /repo && \
    cd /repo && \
    git checkout ${BASE_COMMIT}

RUN git config --global user.email "bench@test" && \
    git config --global user.name "Benchmark"

ENV PYTHONPATH="/repo"
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo