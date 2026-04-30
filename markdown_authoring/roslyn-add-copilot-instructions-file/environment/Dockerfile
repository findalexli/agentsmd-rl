FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/roslyn && \
    cd /workspace/roslyn && \
    git remote add origin https://github.com/dotnet/roslyn.git && \
    git fetch --depth=1 origin 0a431a8a0a7a6f0c1a9f8d822de706376e75ba48 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/roslyn
