FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nf-interpreter && \
    cd /workspace/nf-interpreter && \
    git remote add origin https://github.com/nanoframework/nf-interpreter.git && \
    git fetch --depth=1 origin ca990fd548dab63948d380c20a59deb2b036ee23 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nf-interpreter
