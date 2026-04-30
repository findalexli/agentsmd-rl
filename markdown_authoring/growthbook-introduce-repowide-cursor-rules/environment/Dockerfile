FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/growthbook && \
    cd /workspace/growthbook && \
    git remote add origin https://github.com/growthbook/growthbook.git && \
    git fetch --depth=1 origin 6cb3760e381bd1bb99f67d122fc19bd277f9d5db && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/growthbook
