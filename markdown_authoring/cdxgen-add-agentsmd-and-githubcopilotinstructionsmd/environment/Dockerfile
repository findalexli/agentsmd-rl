FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cdxgen && \
    cd /workspace/cdxgen && \
    git remote add origin https://github.com/cdxgen/cdxgen.git && \
    git fetch --depth=1 origin 6191fbdc3d18c744fbe3b9648903e737b08eb987 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cdxgen
