FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jwx && \
    cd /workspace/jwx && \
    git remote add origin https://github.com/lestrrat-go/jwx.git && \
    git fetch --depth=1 origin 1f715710fa563331b213e2dc81565e9f5e36ab2e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jwx
