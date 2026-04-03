FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/wasp-lang/wasp.git /workspace/wasp && \
    cd /workspace/wasp && \
    git checkout 02e17a0faa6c5297d0f22fc89a84be5ffa6c6665 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/wasp

RUN mkdir -p /logs/verifier
