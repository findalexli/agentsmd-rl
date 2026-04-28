FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcp-for-beginners && \
    cd /workspace/mcp-for-beginners && \
    git remote add origin https://github.com/microsoft/mcp-for-beginners.git && \
    git fetch --depth=1 origin 9d7d14091f94fe2bbd15f998f44091e8af3d7511 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcp-for-beginners
