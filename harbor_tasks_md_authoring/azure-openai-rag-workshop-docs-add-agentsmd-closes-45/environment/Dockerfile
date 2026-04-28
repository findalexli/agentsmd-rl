FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/azure-openai-rag-workshop && \
    cd /workspace/azure-openai-rag-workshop && \
    git remote add origin https://github.com/Azure-Samples/azure-openai-rag-workshop.git && \
    git fetch --depth=1 origin 21b539c1d96b45b96f6fa6662e44952fa2bf6d46 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/azure-openai-rag-workshop
