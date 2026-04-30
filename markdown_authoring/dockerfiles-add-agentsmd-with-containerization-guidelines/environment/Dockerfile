FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dockerfiles && \
    cd /workspace/dockerfiles && \
    git remote add origin https://github.com/jauderho/dockerfiles.git && \
    git fetch --depth=1 origin e14c7f339b354d3ff3d7d2627383134604e3d7d3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dockerfiles
