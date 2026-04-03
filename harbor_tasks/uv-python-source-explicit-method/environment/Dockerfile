FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (parent of merge commit for PR #18569)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin d7da792648a6e8bc2e56162f5890f44333df9ab8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo