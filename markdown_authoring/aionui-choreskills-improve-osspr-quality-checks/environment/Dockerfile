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
    git fetch --depth=1 origin 3ca5bcf558f541c02c49dd4f88c4ab6a25423b77 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/aionui
