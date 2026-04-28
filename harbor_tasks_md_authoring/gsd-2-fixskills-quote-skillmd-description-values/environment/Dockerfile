FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gsd-2 && \
    cd /workspace/gsd-2 && \
    git remote add origin https://github.com/gsd-build/gsd-2.git && \
    git fetch --depth=1 origin 779bb249711bad8270b3a67676f42f170fc32202 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gsd-2
