FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bluefin && \
    cd /workspace/bluefin && \
    git remote add origin https://github.com/ublue-os/bluefin.git && \
    git fetch --depth=1 origin af4a7e718d179e2e3dd7b598d8c1dba8f271485d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bluefin
