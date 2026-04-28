FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/keploy && \
    cd /workspace/keploy && \
    git remote add origin https://github.com/keploy/keploy.git && \
    git fetch --depth=1 origin 874064ecd1a1658a1f41cfa3ecf3c19cf3d77e6a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/keploy
