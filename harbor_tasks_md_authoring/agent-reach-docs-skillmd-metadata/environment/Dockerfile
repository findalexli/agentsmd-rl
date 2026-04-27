FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-reach && \
    cd /workspace/agent-reach && \
    git remote add origin https://github.com/Panniantong/Agent-Reach.git && \
    git fetch --depth=1 origin 70a0bb8af8bbc336c750254a1c5faeb87e082777 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-reach
