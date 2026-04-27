FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-coding-project-boilerplate && \
    cd /workspace/ai-coding-project-boilerplate && \
    git remote add origin https://github.com/shinpr/ai-coding-project-boilerplate.git && \
    git fetch --depth=1 origin 38b111e59bb20ef7290ecb9d493ad030e96bb5b6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-coding-project-boilerplate
