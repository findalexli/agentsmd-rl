FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cursorrules && \
    cd /workspace/cursorrules && \
    git remote add origin https://github.com/kinopeee/cursorrules.git && \
    git fetch --depth=1 origin c1c7e11abc6d9eef75b8d5af99568941b22c2d51 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cursorrules
