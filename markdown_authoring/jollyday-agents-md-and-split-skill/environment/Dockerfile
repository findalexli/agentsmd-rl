FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jollyday && \
    cd /workspace/jollyday && \
    git remote add origin https://github.com/focus-shift/jollyday.git && \
    git fetch --depth=1 origin 1aaef7cea6af7c1cb3d31c36beb7aac47479bca6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jollyday
