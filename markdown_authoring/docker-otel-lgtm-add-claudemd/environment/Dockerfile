FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/docker-otel-lgtm && \
    cd /workspace/docker-otel-lgtm && \
    git remote add origin https://github.com/grafana/docker-otel-lgtm.git && \
    git fetch --depth=1 origin ef715567770b72424299d36229ba9c4827a75d7d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/docker-otel-lgtm
