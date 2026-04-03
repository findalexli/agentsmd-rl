FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

# Clone repo at base commit (before the fix)
RUN git init /repos/uv && \
    cd /repos/uv && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin cedae1aa42c0f1ff59b4e4f988659c52d467d585 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repos/uv