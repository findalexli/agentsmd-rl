FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pai-opencode && \
    cd /workspace/pai-opencode && \
    git remote add origin https://github.com/Steffen025/pai-opencode.git && \
    git fetch --depth=1 origin b9983b0d0e1145cb4bd0e5bbe81e04841b825017 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pai-opencode
