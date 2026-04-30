FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jobset && \
    cd /workspace/jobset && \
    git remote add origin https://github.com/kubernetes-sigs/jobset.git && \
    git fetch --depth=1 origin 94876b5878c83fa3862283ba944044413fcf5fe5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jobset
