FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tinker-cookbook && \
    cd /workspace/tinker-cookbook && \
    git remote add origin https://github.com/thinking-machines-lab/tinker-cookbook.git && \
    git fetch --depth=1 origin d617a7ed2fb85cc98387f1a1b8c30e2a18c1817a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tinker-cookbook
