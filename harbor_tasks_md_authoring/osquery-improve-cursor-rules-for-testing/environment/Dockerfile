FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/osquery && \
    cd /workspace/osquery && \
    git remote add origin https://github.com/osquery/osquery.git && \
    git fetch --depth=1 origin 6f6fe28f37765fdcd57a0e85c06e5959d4fe5718 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/osquery
