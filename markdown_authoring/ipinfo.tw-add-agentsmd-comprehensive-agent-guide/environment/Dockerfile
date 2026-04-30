FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ipinfo.tw && \
    cd /workspace/ipinfo.tw && \
    git remote add origin https://github.com/PeterDaveHello/ipinfo.tw.git && \
    git fetch --depth=1 origin a9ccd30bef8fa289c1be9a712b1e274541116244 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ipinfo.tw
