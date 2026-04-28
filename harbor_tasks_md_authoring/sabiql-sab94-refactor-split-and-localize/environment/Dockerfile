FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sabiql && \
    cd /workspace/sabiql && \
    git remote add origin https://github.com/riii111/sabiql.git && \
    git fetch --depth=1 origin 9f75a6baaf6e94d06075ea81aefb9d7fc234cb62 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sabiql
