FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/worktrunk && \
    cd /workspace/worktrunk && \
    git remote add origin https://github.com/max-sixty/worktrunk.git && \
    git fetch --depth=1 origin 18bea3a32f4b067e4822a62a3c5f13125aa3fcce && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/worktrunk
