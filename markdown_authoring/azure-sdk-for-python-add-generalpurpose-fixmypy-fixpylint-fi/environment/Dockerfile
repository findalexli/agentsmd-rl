FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/azure-sdk-for-python && \
    cd /workspace/azure-sdk-for-python && \
    git remote add origin https://github.com/Azure/azure-sdk-for-python.git && \
    git fetch --depth=1 origin 9011bd1ff2d96f50d6508fc030b35b36bb4cd7e9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/azure-sdk-for-python
