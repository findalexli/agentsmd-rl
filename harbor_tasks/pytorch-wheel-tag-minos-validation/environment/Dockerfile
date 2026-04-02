FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=2a86e1131417aa9fa6b860b03308215bfe2be92c

RUN git clone --filter=blob:none https://github.com/pytorch/pytorch.git /workspace && \
    cd /workspace && \
    git checkout ${BASE_COMMIT}

RUN git config --global user.email "agent@test" && \
    git config --global user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace