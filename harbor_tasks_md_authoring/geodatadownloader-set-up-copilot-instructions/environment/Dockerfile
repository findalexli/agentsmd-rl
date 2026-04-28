FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/geodatadownloader && \
    cd /workspace/geodatadownloader && \
    git remote add origin https://github.com/mchaynes/geodatadownloader.git && \
    git fetch --depth=1 origin 48990ac8ece57a03b9078f51fc87f2c0d7ab4e3f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/geodatadownloader
