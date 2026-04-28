FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dingtalk-workspace-cli && \
    cd /workspace/dingtalk-workspace-cli && \
    git remote add origin https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli.git && \
    git fetch --depth=1 origin ad33a46883be6e7a89bccc36b16a10f097a6ef30 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dingtalk-workspace-cli
