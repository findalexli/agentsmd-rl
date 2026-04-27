FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/aionui && \
    cd /workspace/aionui && \
    git remote add origin https://github.com/iOfficeAI/AionUi.git && \
    git fetch --depth=1 origin 8bb390b1ab999572a7dd1d0eb7e17a83a52a7849 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/aionui
