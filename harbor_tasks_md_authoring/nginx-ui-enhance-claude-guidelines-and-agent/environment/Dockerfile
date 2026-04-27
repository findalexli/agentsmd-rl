FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nginx-ui && \
    cd /workspace/nginx-ui && \
    git remote add origin https://github.com/0xJacky/nginx-ui.git && \
    git fetch --depth=1 origin 79344395f5df3efad97bd021b183569c34c19e46 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nginx-ui
