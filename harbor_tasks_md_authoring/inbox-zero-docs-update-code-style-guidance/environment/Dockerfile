FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/inbox-zero && \
    cd /workspace/inbox-zero && \
    git remote add origin https://github.com/elie222/inbox-zero.git && \
    git fetch --depth=1 origin 0bf8d459a370afbecfe9869d9faaf9ce8a861576 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/inbox-zero
