FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/invokeai && \
    cd /workspace/invokeai && \
    git remote add origin https://github.com/invoke-ai/InvokeAI.git && \
    git fetch --depth=1 origin aeb512f8d9f9ef1281b619a2dc732754b4c61cd9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/invokeai
