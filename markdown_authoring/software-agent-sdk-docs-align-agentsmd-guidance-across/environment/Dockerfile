FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/software-agent-sdk && \
    cd /workspace/software-agent-sdk && \
    git remote add origin https://github.com/OpenHands/software-agent-sdk.git && \
    git fetch --depth=1 origin 14ed6cce4cfa5f1f25d9862b49f33495bd423a44 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/software-agent-sdk
