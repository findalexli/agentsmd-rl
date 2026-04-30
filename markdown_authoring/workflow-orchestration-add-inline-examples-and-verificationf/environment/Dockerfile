FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/workflow-orchestration && \
    cd /workspace/workflow-orchestration && \
    git remote add origin https://github.com/vxcozy/workflow-orchestration.git && \
    git fetch --depth=1 origin 78f5e5dde3eb6d7ad7ce1e1472dd06315dbfd79d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workflow-orchestration
