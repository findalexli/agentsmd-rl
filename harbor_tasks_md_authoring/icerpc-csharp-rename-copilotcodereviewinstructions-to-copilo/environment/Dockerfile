FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/icerpc-csharp && \
    cd /workspace/icerpc-csharp && \
    git remote add origin https://github.com/icerpc/icerpc-csharp.git && \
    git fetch --depth=1 origin f73ae75e25ce035b0f896e7caea7c0dcb6528bcc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/icerpc-csharp
