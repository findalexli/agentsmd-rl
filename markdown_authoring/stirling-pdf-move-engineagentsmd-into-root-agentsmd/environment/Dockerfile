FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stirling-pdf && \
    cd /workspace/stirling-pdf && \
    git remote add origin https://github.com/Stirling-Tools/Stirling-PDF.git && \
    git fetch --depth=1 origin 3b2afe0deb1c50e1e8544ccb7f1ff5d98aa61eb7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stirling-pdf
