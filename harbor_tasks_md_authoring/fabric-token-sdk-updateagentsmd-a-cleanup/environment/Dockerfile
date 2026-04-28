FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fabric-token-sdk && \
    cd /workspace/fabric-token-sdk && \
    git remote add origin https://github.com/hyperledger-labs/fabric-token-sdk.git && \
    git fetch --depth=1 origin 953ffb6237a7b9b137fc17b5556386282004657c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fabric-token-sdk
