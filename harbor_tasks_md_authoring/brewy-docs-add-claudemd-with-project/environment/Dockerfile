FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/brewy && \
    cd /workspace/brewy && \
    git remote add origin https://github.com/starhaven-io/Brewy.git && \
    git fetch --depth=1 origin 782826eb9b81c5b265f0b77acd3fbe71fe851f6e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/brewy
