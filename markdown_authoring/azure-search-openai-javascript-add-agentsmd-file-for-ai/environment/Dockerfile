FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/azure-search-openai-javascript && \
    cd /workspace/azure-search-openai-javascript && \
    git remote add origin https://github.com/Azure-Samples/azure-search-openai-javascript.git && \
    git fetch --depth=1 origin 69c2751c966220a2e3ec3435a4dd8c0e566c42c7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/azure-search-openai-javascript
