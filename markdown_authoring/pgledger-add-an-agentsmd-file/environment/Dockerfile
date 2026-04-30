FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pgledger && \
    cd /workspace/pgledger && \
    git remote add origin https://github.com/pgr0ss/pgledger.git && \
    git fetch --depth=1 origin 83d9fa20200b4e13a075531fcff3ee9a7fb7ac8d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pgledger
