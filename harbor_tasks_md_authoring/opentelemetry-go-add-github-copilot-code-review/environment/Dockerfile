FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/opentelemetry-go && \
    cd /workspace/opentelemetry-go && \
    git remote add origin https://github.com/open-telemetry/opentelemetry-go.git && \
    git fetch --depth=1 origin c56c84380c4569ae465dcfc32064883172f86c66 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opentelemetry-go
