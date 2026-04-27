FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/commonly && \
    cd /workspace/commonly && \
    git remote add origin https://github.com/Team-Commonly/commonly.git && \
    git fetch --depth=1 origin ed2490e4f8fdc4325cbe3d09c3a7ff938dc0652b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/commonly
