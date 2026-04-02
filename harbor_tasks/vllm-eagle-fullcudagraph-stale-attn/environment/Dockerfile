FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=vllm-project/vllm
ARG BASE_COMMIT=44a6528028ad79951de08b6a7928f6c05788d00d

RUN git clone --filter=blob:none https://github.com/${REPO}.git /repo && \
    cd /repo && \
    git checkout ${BASE_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for the agent
RUN git config user.email "agent@example.com" && \
    git config user.name "Agent"

ENV PYTHONPATH=/repo