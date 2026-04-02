FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at the base commit (before the fix)
ARG BASE_COMMIT=cde48c8ac8eb13e8eff5cfb5c9fc39dad69c4f19

RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout ${BASE_COMMIT} \
    && git config user.email "test@test.com" \
    && git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo