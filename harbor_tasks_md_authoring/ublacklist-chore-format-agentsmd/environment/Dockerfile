FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ublacklist && \
    cd /workspace/ublacklist && \
    git remote add origin https://github.com/iorate/ublacklist.git && \
    git fetch --depth=1 origin c37e7e2a9073b7e24d9d8fffd0d947c9024fab33 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ublacklist
