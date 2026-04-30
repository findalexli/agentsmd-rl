FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agentsys && \
    cd /workspace/agentsys && \
    git remote add origin https://github.com/agent-sh/agentsys.git && \
    git fetch --depth=1 origin 16c5c8b9c525b25a78ffe40f9b4353407983d644 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agentsys
