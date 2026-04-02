FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before the fix)
RUN git clone --no-checkout https://github.com/astral-sh/uv.git /repo && \
    cd /repo && \
    git checkout d0f2f3babc7c892958e93419ad6065df0deb2112

RUN mkdir -p /logs/verifier

WORKDIR /repo

ENV PYTHONPATH=/repo