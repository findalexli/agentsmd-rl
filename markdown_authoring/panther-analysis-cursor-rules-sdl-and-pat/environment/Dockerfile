FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/panther-analysis && \
    cd /workspace/panther-analysis && \
    git remote add origin https://github.com/panther-labs/panther-analysis.git && \
    git fetch --depth=1 origin d48f5ab6b17eefa97f383d3d493d63e211ebf1f2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/panther-analysis
