FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ragflow && \
    cd /workspace/ragflow && \
    git remote add origin https://github.com/infiniflow/ragflow.git && \
    git fetch --depth=1 origin 4dcc42e0e14ad4a93373f08b325757cba285ac54 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ragflow
