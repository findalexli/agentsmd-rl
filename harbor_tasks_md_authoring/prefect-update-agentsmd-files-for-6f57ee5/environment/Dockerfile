FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prefect && \
    cd /workspace/prefect && \
    git remote add origin https://github.com/prefecthq/prefect.git && \
    git fetch --depth=1 origin 6f57ee57ea4e4e316703f2818d02f4e7cee3b1fc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prefect
