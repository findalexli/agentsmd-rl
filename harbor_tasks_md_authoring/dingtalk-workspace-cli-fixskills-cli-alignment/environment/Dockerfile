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
    git fetch --depth=1 origin d13d1eed160ab5154b5889768ac1fbd2ad9eb958 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dingtalk-workspace-cli
