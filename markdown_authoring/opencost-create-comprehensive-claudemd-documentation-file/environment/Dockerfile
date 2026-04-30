FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/opencost && \
    cd /workspace/opencost && \
    git remote add origin https://github.com/opencost/opencost.git && \
    git fetch --depth=1 origin d3bd2fd27f11d3b0a1b2f924e2dbed0aedc8ca97 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencost
