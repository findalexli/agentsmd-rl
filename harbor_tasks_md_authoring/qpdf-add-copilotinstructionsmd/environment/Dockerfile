FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/qpdf && \
    cd /workspace/qpdf && \
    git remote add origin https://github.com/qpdf/qpdf.git && \
    git fetch --depth=1 origin 35ca7efe103fb65d2c00eb9b6deb29d3d95bfc0c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/qpdf
