FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openhab-webui && \
    cd /workspace/openhab-webui && \
    git remote add origin https://github.com/openhab/openhab-webui.git && \
    git fetch --depth=1 origin 38c0c728f233ecb135396b7b5a5dd6e37a106ff6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhab-webui
