FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/auto-author-assign && \
    cd /workspace/auto-author-assign && \
    git remote add origin https://github.com/toshimaru/auto-author-assign.git && \
    git fetch --depth=1 origin 5cd66f093de6691e0812ef186b7492589b0b7866 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/auto-author-assign
