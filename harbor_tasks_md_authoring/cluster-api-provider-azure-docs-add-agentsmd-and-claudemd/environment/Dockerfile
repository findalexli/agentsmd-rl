FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cluster-api-provider-azure && \
    cd /workspace/cluster-api-provider-azure && \
    git remote add origin https://github.com/kubernetes-sigs/cluster-api-provider-azure.git && \
    git fetch --depth=1 origin e12a33ae8945be5b19e5f895270ee87e6fa72114 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cluster-api-provider-azure
