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
    git fetch --depth=1 origin 2ec1bcb857e249c98580658a17b69288416e9d85 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tinker-cookbook
