FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ag-charts && \
    cd /workspace/ag-charts && \
    git remote add origin https://github.com/ag-grid/ag-charts.git && \
    git fetch --depth=1 origin 5c86dfe3c6c5dd6e377f7f9aa02e514adbe6fb75 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ag-charts
