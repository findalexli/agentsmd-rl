FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=8eaba043803b82549bf4fb42d5e03099be2eb1d9

RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN git config --global user.email "agent@test" && \
    git config --global user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace