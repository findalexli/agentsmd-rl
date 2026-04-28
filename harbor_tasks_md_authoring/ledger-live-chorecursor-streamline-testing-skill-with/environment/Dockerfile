FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ledger-live && \
    cd /workspace/ledger-live && \
    git remote add origin https://github.com/LedgerHQ/ledger-live.git && \
    git fetch --depth=1 origin 834c7efbb32488892e2467ec57241dbfaac203ab && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ledger-live
