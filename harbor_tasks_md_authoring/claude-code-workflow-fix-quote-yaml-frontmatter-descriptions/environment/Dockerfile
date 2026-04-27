FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-workflow && \
    cd /workspace/claude-code-workflow && \
    git remote add origin https://github.com/catlog22/Claude-Code-Workflow.git && \
    git fetch --depth=1 origin a45c672d3069d6d51808fd3ca72f9ffd39bdc44c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-workflow
