FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agents-at-scale-ark && \
    cd /workspace/agents-at-scale-ark && \
    git remote add origin https://github.com/mckinsey/agents-at-scale-ark.git && \
    git fetch --depth=1 origin 5e4eb9d855cc65af10f870172ab171806d32b3a4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agents-at-scale-ark
