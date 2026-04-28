FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bitcoin-safe && \
    cd /workspace/bitcoin-safe && \
    git remote add origin https://github.com/andreasgriffin/bitcoin-safe.git && \
    git fetch --depth=1 origin 679b3f1448d100cc5cf800965eab2132f0081181 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bitcoin-safe
