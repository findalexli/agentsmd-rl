FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/everything-claude-code && \
    cd /workspace/everything-claude-code && \
    git remote add origin https://github.com/affaan-m/everything-claude-code.git && \
    git fetch --depth=1 origin af51fcacb70d42ed52ba8111026d9b0f0e49b364 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/everything-claude-code
