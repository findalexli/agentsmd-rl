FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-plugins && \
    cd /workspace/agent-plugins && \
    git remote add origin https://github.com/awslabs/agent-plugins.git && \
    git fetch --depth=1 origin b2a8183b2cfaed906cbc77d77c560d87273d5b35 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-plugins
