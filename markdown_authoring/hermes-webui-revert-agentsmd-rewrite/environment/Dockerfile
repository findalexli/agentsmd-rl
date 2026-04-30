FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hermes-webui && \
    cd /workspace/hermes-webui && \
    git remote add origin https://github.com/nesquena/hermes-webui.git && \
    git fetch --depth=1 origin f2be17a98d77daa0c623b7c1143b0f197f822953 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hermes-webui
