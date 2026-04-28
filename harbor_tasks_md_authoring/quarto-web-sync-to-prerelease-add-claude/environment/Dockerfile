FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/quarto-web && \
    cd /workspace/quarto-web && \
    git remote add origin https://github.com/quarto-dev/quarto-web.git && \
    git fetch --depth=1 origin 5c2a7d6ab4634ff8b3ff64a072cb757b5909e943 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/quarto-web
