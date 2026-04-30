FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prd-taskmaster && \
    cd /workspace/prd-taskmaster && \
    git remote add origin https://github.com/anombyte93/prd-taskmaster.git && \
    git fetch --depth=1 origin f2437f01e7663d19343489e1d30fc3e895ee713a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prd-taskmaster
