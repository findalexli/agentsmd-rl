FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sdk-generator && \
    cd /workspace/sdk-generator && \
    git remote add origin https://github.com/appwrite/sdk-generator.git && \
    git fetch --depth=1 origin b31e6b4209ecad46d2fef509dc59f1945d0e83cb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sdk-generator
