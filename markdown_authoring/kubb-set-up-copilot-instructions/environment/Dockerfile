FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kubb && \
    cd /workspace/kubb && \
    git remote add origin https://github.com/kubb-labs/kubb.git && \
    git fetch --depth=1 origin c3b24e3aa2255e69b0d64e83b50ee4e4fd377370 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kubb
