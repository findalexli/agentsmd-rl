FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kgateway && \
    cd /workspace/kgateway && \
    git remote add origin https://github.com/kgateway-dev/kgateway.git && \
    git fetch --depth=1 origin 389d36af294764167bda2dd2157e6cf0ccaabe3e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kgateway
