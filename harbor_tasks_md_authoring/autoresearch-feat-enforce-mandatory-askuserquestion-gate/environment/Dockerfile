FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/autoresearch && \
    cd /workspace/autoresearch && \
    git remote add origin https://github.com/uditgoenka/autoresearch.git && \
    git fetch --depth=1 origin 4855087d4a1f46f552cc8a4c34d805bc86b15e95 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/autoresearch
