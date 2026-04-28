FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/causalpy && \
    cd /workspace/causalpy && \
    git remote add origin https://github.com/pymc-labs/CausalPy.git && \
    git fetch --depth=1 origin 6795c1465f065a56b1cd9c8d596a50ce5f9a2269 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/causalpy
