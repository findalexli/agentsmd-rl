FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/open-wearables && \
    cd /workspace/open-wearables && \
    git remote add origin https://github.com/the-momentum/open-wearables.git && \
    git fetch --depth=1 origin 0356dbf09e4172c6f381da55dcc57d43a31b9080 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/open-wearables
