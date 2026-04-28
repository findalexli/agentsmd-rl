FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gitops-promoter && \
    cd /workspace/gitops-promoter && \
    git remote add origin https://github.com/argoproj-labs/gitops-promoter.git && \
    git fetch --depth=1 origin 4a47308190e1a72c507b75dfa5f39a6a4c8fe046 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gitops-promoter
