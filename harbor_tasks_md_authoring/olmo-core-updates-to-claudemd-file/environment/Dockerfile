FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/olmo-core && \
    cd /workspace/olmo-core && \
    git remote add origin https://github.com/allenai/OLMo-core.git && \
    git fetch --depth=1 origin d69433d41bbdec1ae687fb0e5d298f2ee268fcad && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/olmo-core
