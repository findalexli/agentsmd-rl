FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git remote add origin https://github.com/lobehub/lobe-chat.git && \
    git fetch --depth=1 origin 998c22890d4b5c6189418f94916cd036863fdfd8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lobe-chat
