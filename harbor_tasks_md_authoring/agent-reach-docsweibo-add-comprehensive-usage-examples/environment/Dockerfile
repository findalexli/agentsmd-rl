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
    git fetch --depth=1 origin 90bb4e0266b81c2665c2c440f55412c75a2d2fad && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-reach
