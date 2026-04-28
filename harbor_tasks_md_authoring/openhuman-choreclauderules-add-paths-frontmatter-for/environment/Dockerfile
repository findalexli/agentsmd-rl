FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openhuman && \
    cd /workspace/openhuman && \
    git remote add origin https://github.com/tinyhumansai/openhuman.git && \
    git fetch --depth=1 origin 3dc0d0db64baf26b4d7c29062a79a12cc7b4bfbf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhuman
