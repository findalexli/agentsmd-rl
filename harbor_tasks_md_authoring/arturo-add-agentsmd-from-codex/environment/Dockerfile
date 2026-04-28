FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/arturo && \
    cd /workspace/arturo && \
    git remote add origin https://github.com/arturo-lang/arturo.git && \
    git fetch --depth=1 origin 96f0774161ba4e63a491820f6aeb7bdab2f0aec2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/arturo
