FROM rust:1-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 09f645d49f1337866d63e62570cb9a43a4a875b3 && \
    git checkout FETCH_HEAD

ENV PYTHONPATH="/workspace/ruff"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/ruff