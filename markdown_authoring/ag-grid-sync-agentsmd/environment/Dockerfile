FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ag-grid && \
    cd /workspace/ag-grid && \
    git remote add origin https://github.com/ag-grid/ag-grid.git && \
    git fetch --depth=1 origin d1e506c6f21b3ae84c36e45018515d80621c5822 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ag-grid
