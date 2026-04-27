FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-marketing-skills && \
    cd /workspace/claude-code-marketing-skills && \
    git remote add origin https://github.com/cognyai/claude-code-marketing-skills.git && \
    git fetch --depth=1 origin f8fbb6e08eb1f5166bfb935d1bd7f5db41890946 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-marketing-skills
