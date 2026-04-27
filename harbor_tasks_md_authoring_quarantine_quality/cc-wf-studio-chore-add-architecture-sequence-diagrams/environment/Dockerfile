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
    git fetch --depth=1 origin 38e11e0b30400370ead4621aea9f920a5bd596dd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cc-wf-studio
