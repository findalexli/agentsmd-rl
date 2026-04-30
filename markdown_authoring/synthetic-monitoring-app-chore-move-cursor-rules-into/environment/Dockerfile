FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/synthetic-monitoring-app && \
    cd /workspace/synthetic-monitoring-app && \
    git remote add origin https://github.com/grafana/synthetic-monitoring-app.git && \
    git fetch --depth=1 origin a197c7a5805b9382c773197d51ea2026b7940544 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/synthetic-monitoring-app
