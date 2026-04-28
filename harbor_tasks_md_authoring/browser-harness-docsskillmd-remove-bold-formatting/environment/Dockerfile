FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/browser-harness && \
    cd /workspace/browser-harness && \
    git remote add origin https://github.com/browser-use/browser-harness.git && \
    git fetch --depth=1 origin ba8b22f1ff3db93546b5a194a1978914c8ceb0f2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/browser-harness
