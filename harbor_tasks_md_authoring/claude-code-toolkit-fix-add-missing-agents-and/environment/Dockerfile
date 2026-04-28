FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-toolkit && \
    cd /workspace/claude-code-toolkit && \
    git remote add origin https://github.com/notque/claude-code-toolkit.git && \
    git fetch --depth=1 origin 1d8cf97feb4b79f20e53bce0a22e77b935277266 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-toolkit
