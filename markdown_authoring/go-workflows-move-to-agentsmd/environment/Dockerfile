FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/go-workflows && \
    cd /workspace/go-workflows && \
    git remote add origin https://github.com/cschleiden/go-workflows.git && \
    git fetch --depth=1 origin 33a43f6bb3e6bbabc14593cc3dafcf7660220740 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/go-workflows
