FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ARG REPO_COMMIT=c34593f9512a0be2eb9d252303a7bd12f47f881f
RUN git clone https://github.com/sgl-project/sglang.git /workspace && \
    cd /workspace && \
    git checkout ${REPO_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /workspace

ENV PYTHONPATH="/workspace/python:${PYTHONPATH}"