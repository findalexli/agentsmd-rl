FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cc-wf-studio && \
    cd /workspace/cc-wf-studio && \
    git remote add origin https://github.com/breaking-brake/cc-wf-studio.git && \
    git fetch --depth=1 origin 4647daa6d0a5b58cb32c564674b11f3067f39716 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cc-wf-studio
