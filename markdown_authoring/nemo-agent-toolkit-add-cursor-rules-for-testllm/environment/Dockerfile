FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nemo-agent-toolkit && \
    cd /workspace/nemo-agent-toolkit && \
    git remote add origin https://github.com/NVIDIA/NeMo-Agent-Toolkit.git && \
    git fetch --depth=1 origin c0e7ba2e0021eb0c062aec1cc4614d79da174613 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nemo-agent-toolkit
