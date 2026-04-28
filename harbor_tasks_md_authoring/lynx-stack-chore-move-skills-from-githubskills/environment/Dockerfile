FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lynx-stack && \
    cd /workspace/lynx-stack && \
    git remote add origin https://github.com/lynx-family/lynx-stack.git && \
    git fetch --depth=1 origin 57c7fa3d74cc33efe2ac1af6a060fe0f72cf8650 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lynx-stack
