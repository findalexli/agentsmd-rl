FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin c17877c2ad39f8f736d5ea8a34f98e562843fc83 && \
    git checkout FETCH_HEAD

# Install transformers in editable mode (core + minimal deps)
RUN pip install --no-cache-dir -e /workspace/transformers 2>&1 | tail -3

# Install test tooling (xdist needed for conftest.py plugin compat)
RUN pip install --no-cache-dir ruff pytest pytest-json-ctrf pytest-xdist 2>&1 | tail -3

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/transformers
