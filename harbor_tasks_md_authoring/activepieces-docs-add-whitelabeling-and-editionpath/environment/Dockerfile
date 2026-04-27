FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/activepieces && \
    cd /workspace/activepieces && \
    git remote add origin https://github.com/activepieces/activepieces.git && \
    git fetch --depth=1 origin 2c4f3316ae297360469f4f0bf747fa9254fc0a9d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/activepieces
