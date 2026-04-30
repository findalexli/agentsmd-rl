FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/posixutils-rs && \
    cd /workspace/posixutils-rs && \
    git remote add origin https://github.com/rustcoreutils/posixutils-rs.git && \
    git fetch --depth=1 origin a804ba4a5a87ebfbc41993860975ce2f9658294e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/posixutils-rs
