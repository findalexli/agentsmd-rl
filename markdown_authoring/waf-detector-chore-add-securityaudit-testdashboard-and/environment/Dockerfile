FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/waf-detector && \
    cd /workspace/waf-detector && \
    git remote add origin https://github.com/ammarion/waf-detector.git && \
    git fetch --depth=1 origin bfa02d62dee8e1f778cc8931c0933b3a6461feab && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/waf-detector
