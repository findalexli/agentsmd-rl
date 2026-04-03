FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin b3d7942fbaedda791668d7fe42eaaa323ed7a089 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install CPU-only torch + transformers with base deps
RUN pip install --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -e .

# Install ruff for style checks and pytest for test runner
RUN pip install --no-cache-dir ruff pytest pytest-json-ctrf

RUN git config user.name "solver" && \
    git config user.email "solver@bench"

ENV PYTHONPATH=/repo/src