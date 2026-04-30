FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/system-deps && \
    cd /workspace/system-deps && \
    git remote add origin https://github.com/gdesmott/system-deps.git && \
    git fetch --depth=1 origin f5592dd43672bcf0197f52f79f77b1144493e872 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/system-deps
