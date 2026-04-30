FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/elasticsearch-js && \
    cd /workspace/elasticsearch-js && \
    git remote add origin https://github.com/elastic/elasticsearch-js.git && \
    git fetch --depth=1 origin d14abb26498777e63a80946648cffc38f4e19b1b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/elasticsearch-js
