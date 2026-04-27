FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rdc-cli && \
    cd /workspace/rdc-cli && \
    git remote add origin https://github.com/BANANASJIM/rdc-cli.git && \
    git fetch --depth=1 origin 219700c946853c1754654be4023bdee4b9e4ff25 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rdc-cli
