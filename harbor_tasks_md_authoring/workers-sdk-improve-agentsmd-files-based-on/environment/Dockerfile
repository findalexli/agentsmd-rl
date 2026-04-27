FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git remote add origin https://github.com/cloudflare/workers-sdk.git && \
    git fetch --depth=1 origin 5eff8c14f08696e5a832875a35e214969aa55b9b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workers-sdk
