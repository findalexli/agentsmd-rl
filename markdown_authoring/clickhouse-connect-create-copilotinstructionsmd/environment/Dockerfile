FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/clickhouse-connect && \
    cd /workspace/clickhouse-connect && \
    git remote add origin https://github.com/ClickHouse/clickhouse-connect.git && \
    git fetch --depth=1 origin 904c9c76a4b3eddd2c79cb5091eeea2004f21756 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/clickhouse-connect
