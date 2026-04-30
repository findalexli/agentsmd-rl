FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/codecapy && \
    cd /workspace/codecapy && \
    git remote add origin https://github.com/Scrapybara/codecapy.git && \
    git fetch --depth=1 origin 5bfd39ebf9156b54bc2fdaeed7fa61d789924055 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/codecapy
