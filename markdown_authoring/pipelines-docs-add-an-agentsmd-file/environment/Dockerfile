FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pipelines && \
    cd /workspace/pipelines && \
    git remote add origin https://github.com/kubeflow/pipelines.git && \
    git fetch --depth=1 origin 4471829cdbe0761a79e661ac83ef0139abcb3d0c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pipelines
