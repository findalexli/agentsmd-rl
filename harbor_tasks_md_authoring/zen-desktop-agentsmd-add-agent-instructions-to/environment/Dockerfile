FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/zen-desktop && \
    cd /workspace/zen-desktop && \
    git remote add origin https://github.com/irbis-sh/zen-desktop.git && \
    git fetch --depth=1 origin 7a24112c3d02434fcfca208e8d8d7e09d7b03292 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/zen-desktop
