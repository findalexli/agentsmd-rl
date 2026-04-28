FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shardingsphere && \
    cd /workspace/shardingsphere && \
    git remote add origin https://github.com/apache/shardingsphere.git && \
    git fetch --depth=1 origin 82805e27c8677a2abbb32952a12bb6bbbd56ce00 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shardingsphere
