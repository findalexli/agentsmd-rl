FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/context-engineering-kit && \
    cd /workspace/context-engineering-kit && \
    git remote add origin https://github.com/NeoLabHQ/context-engineering-kit.git && \
    git fetch --depth=1 origin 554814cfd47755379170dd8686d9391822e3ea83 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/context-engineering-kit
