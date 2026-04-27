FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cog-second-brain && \
    cd /workspace/cog-second-brain && \
    git remote add origin https://github.com/huytieu/COG-second-brain.git && \
    git fetch --depth=1 origin 20578724a4e43c6c8384cc812da7a49bfac2350e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cog-second-brain
