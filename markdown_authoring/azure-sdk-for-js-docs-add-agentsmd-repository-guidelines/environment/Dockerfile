FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/azure-sdk-for-js && \
    cd /workspace/azure-sdk-for-js && \
    git remote add origin https://github.com/Azure/azure-sdk-for-js.git && \
    git fetch --depth=1 origin a007364e5edf3192893809ce3926c0826ca64964 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/azure-sdk-for-js
