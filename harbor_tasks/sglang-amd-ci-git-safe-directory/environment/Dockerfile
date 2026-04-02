FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

# Shallow-fetch sglang at the base commit (before the fix)
RUN git init /workspace/sglang \
    && cd /workspace/sglang \
    && git remote add origin https://github.com/sgl-project/sglang.git \
    && git fetch --depth 1 origin 6f2b51ade1b1d072ee7e8d2727f1dbaec0f496ae \
    && git checkout FETCH_HEAD

ENV PYTHONPATH="/workspace/sglang:${PYTHONPATH:-}"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang