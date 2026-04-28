FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pyautolens && \
    cd /workspace/pyautolens && \
    git remote add origin https://github.com/PyAutoLabs/PyAutoLens.git && \
    git fetch --depth=1 origin 4242060559f56baefec38e137bcf126a136b8fb2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pyautolens
