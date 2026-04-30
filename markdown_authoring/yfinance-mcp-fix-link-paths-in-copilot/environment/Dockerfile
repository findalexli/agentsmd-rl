FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/yfinance-mcp && \
    cd /workspace/yfinance-mcp && \
    git remote add origin https://github.com/narumiruna/yfinance-mcp.git && \
    git fetch --depth=1 origin 5f4b27f9d638a2213f045ff84c191b14c6d61dc6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/yfinance-mcp
