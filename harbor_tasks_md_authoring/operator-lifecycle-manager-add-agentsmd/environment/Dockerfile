FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/operator-lifecycle-manager && \
    cd /workspace/operator-lifecycle-manager && \
    git remote add origin https://github.com/operator-framework/operator-lifecycle-manager.git && \
    git fetch --depth=1 origin 47ef860077c662d13c3fd5e8a72879b4d33ba51f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/operator-lifecycle-manager
