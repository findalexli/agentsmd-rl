FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ethskills && \
    cd /workspace/ethskills && \
    git remote add origin https://github.com/austintgriffith/ethskills.git && \
    git fetch --depth=1 origin 58d804f49008c7b7df6578f118f1b47cb7b6eb4c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ethskills
