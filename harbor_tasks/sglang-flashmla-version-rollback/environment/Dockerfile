FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (BEFORE the fix)
RUN git clone https://github.com/sgl-project/sglang.git /workspace/sglang \
    && cd /workspace/sglang \
    && git checkout 7c7b2a8c97816b84c6c90ebe28e7e1a9ea334888 \
    && git config user.name "test" \
    && git config user.email "test@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH:-}"