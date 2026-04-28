FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/htk8s && \
    cd /workspace/htk8s && \
    git remote add origin https://github.com/fabito/htk8s.git && \
    git fetch --depth=1 origin e4c8257e49cc5eb2fd13d63872dd561aca9ecebc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/htk8s
