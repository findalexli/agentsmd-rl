FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shapecrawler && \
    cd /workspace/shapecrawler && \
    git remote add origin https://github.com/ShapeCrawler/ShapeCrawler.git && \
    git fetch --depth=1 origin 51e3b23506b35d893986ae9956773d1404a12b4c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shapecrawler
