FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prisma-next && \
    cd /workspace/prisma-next && \
    git remote add origin https://github.com/prisma/prisma-next.git && \
    git fetch --depth=1 origin ecd9328ea9607eac81ca500456127af56b62d295 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prisma-next
