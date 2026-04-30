FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ifc-lite && \
    cd /workspace/ifc-lite && \
    git remote add origin https://github.com/louistrue/ifc-lite.git && \
    git fetch --depth=1 origin 74b9461c57e577b8feac64e00432b9b6c6f5feec && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ifc-lite
