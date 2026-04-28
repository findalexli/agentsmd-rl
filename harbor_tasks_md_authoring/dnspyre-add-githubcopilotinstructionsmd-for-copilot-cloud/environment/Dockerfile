FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dnspyre && \
    cd /workspace/dnspyre && \
    git remote add origin https://github.com/Tantalor93/dnspyre.git && \
    git fetch --depth=1 origin 6156ee302e5d888a89e121e9333efdd5f64f1759 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dnspyre
