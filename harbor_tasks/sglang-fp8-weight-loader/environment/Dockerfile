FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (BEFORE the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin e6071e60c0975e6c47f056e96d324918c3e5aed5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH:-}"