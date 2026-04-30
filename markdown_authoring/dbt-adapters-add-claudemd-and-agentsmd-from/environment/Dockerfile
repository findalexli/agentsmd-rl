FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dbt-adapters && \
    cd /workspace/dbt-adapters && \
    git remote add origin https://github.com/dbt-labs/dbt-adapters.git && \
    git fetch --depth=1 origin 0befd9a06f0b7fc6aa1f1fcaa019887bed907db3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dbt-adapters
