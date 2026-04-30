FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pg-aiguide && \
    cd /workspace/pg-aiguide && \
    git remote add origin https://github.com/timescale/pg-aiguide.git && \
    git fetch --depth=1 origin 60a60afe8cdc1a36cea5ab736dd1260db7a957d9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pg-aiguide
