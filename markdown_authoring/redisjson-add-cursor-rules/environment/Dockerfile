FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/redisjson && \
    cd /workspace/redisjson && \
    git remote add origin https://github.com/RedisJSON/RedisJSON.git && \
    git fetch --depth=1 origin 85bb358175da2f3d136457e5f2b0d81ddf3c5ded && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/redisjson
