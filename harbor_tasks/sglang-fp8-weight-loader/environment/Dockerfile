FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (BEFORE the fix)
RUN git clone https://github.com/sgl-project/sglang.git /workspace/sglang \
    && cd /workspace/sglang \
    && git checkout e6071e60c0975e6c47f056e96d324918c3e5aed5 \
    && git config user.name "test" \
    && git config user.email "test@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH:-}"