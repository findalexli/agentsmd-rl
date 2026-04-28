FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/restsharp && \
    cd /workspace/restsharp && \
    git remote add origin https://github.com/restsharp/RestSharp.git && \
    git fetch --depth=1 origin eb907af891c02a173f128e37f2ea1bb8e912bde0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/restsharp
