FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/generative-ai-with-javascript && \
    cd /workspace/generative-ai-with-javascript && \
    git remote add origin https://github.com/microsoft/generative-ai-with-javascript.git && \
    git fetch --depth=1 origin 81217323de776d9594d9611249b89efae9294e7c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/generative-ai-with-javascript
