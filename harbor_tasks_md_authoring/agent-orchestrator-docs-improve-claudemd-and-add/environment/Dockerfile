FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-orchestrator && \
    cd /workspace/agent-orchestrator && \
    git remote add origin https://github.com/ComposioHQ/agent-orchestrator.git && \
    git fetch --depth=1 origin 8e5b23e6a064a9f08e41dd980c7183af001365d8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-orchestrator
