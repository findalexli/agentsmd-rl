FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/monorepo && \
    cd /workspace/monorepo && \
    git remote add origin https://github.com/inversify/monorepo.git && \
    git fetch --depth=1 origin 662a57154b0ea59d2c949e30366fe5fbbf970f9e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/monorepo
