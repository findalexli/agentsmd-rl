FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/angular/angular.git /workspace/angular \
    && cd /workspace/angular \
    && git checkout b82901f8f99469a8ff4a0ec54ef78d94c7543f5a

RUN mkdir -p /logs/verifier

WORKDIR /workspace/angular
