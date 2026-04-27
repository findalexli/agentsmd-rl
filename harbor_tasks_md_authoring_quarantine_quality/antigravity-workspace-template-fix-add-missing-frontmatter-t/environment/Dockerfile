FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/antigravity-workspace-template && \
    cd /workspace/antigravity-workspace-template && \
    git remote add origin https://github.com/study8677/antigravity-workspace-template.git && \
    git fetch --depth=1 origin 08ffd3554b001d3aa3f2b5c86666b4fb7c313c6c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/antigravity-workspace-template
