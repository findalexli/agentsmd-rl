FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/continuous-claude-v3 && \
    cd /workspace/continuous-claude-v3 && \
    git remote add origin https://github.com/parcadei/Continuous-Claude-v3.git && \
    git fetch --depth=1 origin 4c3528fbfb6f1530dfbde85174a467d96f0cbe12 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/continuous-claude-v3
