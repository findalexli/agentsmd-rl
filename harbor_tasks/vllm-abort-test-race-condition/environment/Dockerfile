FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=vllm-project/vllm
ARG COMMIT=171775f306a333a9cf105bfd533bf3e113d401d9

RUN git clone --filter=blob:none https://github.com/${REPO}.git /repo && \
    cd /repo && \
    git checkout ${COMMIT} && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

ENV PYTHONPATH=/repo
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo