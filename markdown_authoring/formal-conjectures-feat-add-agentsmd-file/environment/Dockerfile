FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/formal-conjectures && \
    cd /workspace/formal-conjectures && \
    git remote add origin https://github.com/google-deepmind/formal-conjectures.git && \
    git fetch --depth=1 origin 6bbfdded5034be8991b3a4ea1d53c397b8f55901 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/formal-conjectures
