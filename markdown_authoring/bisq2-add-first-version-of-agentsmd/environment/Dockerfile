FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bisq2 && \
    cd /workspace/bisq2 && \
    git remote add origin https://github.com/bisq-network/bisq2.git && \
    git fetch --depth=1 origin 4538a0d4e3e814cec6d5a8e122acacaa2e1297b2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bisq2
