FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bifrost && \
    cd /workspace/bifrost && \
    git remote add origin https://github.com/maximhq/bifrost.git && \
    git fetch --depth=1 origin 63db5746f524954b90ac7a1d9c3ce35422aa5906 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bifrost
