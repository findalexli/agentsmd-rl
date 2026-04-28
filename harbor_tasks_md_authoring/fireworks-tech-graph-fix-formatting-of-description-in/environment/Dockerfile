FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fireworks-tech-graph && \
    cd /workspace/fireworks-tech-graph && \
    git remote add origin https://github.com/yizhiyanhua-ai/fireworks-tech-graph.git && \
    git fetch --depth=1 origin 27f41d98883113affbb28a2ebfff4b566e3cc819 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fireworks-tech-graph
