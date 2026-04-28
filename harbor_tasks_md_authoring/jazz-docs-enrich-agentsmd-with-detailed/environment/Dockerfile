FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jazz && \
    cd /workspace/jazz && \
    git remote add origin https://github.com/garden-co/jazz.git && \
    git fetch --depth=1 origin 6ae95c60d365b0f2e87c9a22fefc2f8a2fe963ea && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jazz
