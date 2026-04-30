FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dtvm && \
    cd /workspace/dtvm && \
    git remote add origin https://github.com/DTVMStack/DTVM.git && \
    git fetch --depth=1 origin a21b40fd9fc64e9928f066551767e396d8198863 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dtvm
